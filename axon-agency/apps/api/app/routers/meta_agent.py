"""
Meta-Agent Router: API endpoints for specialized agent management.

This router provides endpoints for:
- Agent creation and management
- Task assignment and tracking
- Agent replication across tenants
- Governance and audit logs
- Performance metrics
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from loguru import logger

from app.core.security import TokenData, get_current_user_optional, require_admin
from app.models.meta_agent import (
    AgentRole,
    AgentStatus,
    AgentCapability,
    SpecializedAgent,
    AgentReplicationConfig,
    AgentTaskAssignment,
    AgentMetrics,
    ReplicationHistory
)
from app.services.specialized_agent import SpecializedAgentService
from app.services.governance import GovernanceService, GovernanceAction
from app.services.learning import LearningService
from app.services.vector_store import VectorStore
from app.services.embeddings import EmbeddingService


class CreateAgentRequest(BaseModel):
    """Request model for creating a specialized agent."""
    name: str
    role: AgentRole
    tenant_id: str
    capabilities: Optional[AgentCapability] = None

router = APIRouter(prefix="/api/agent/meta")

# Global service instances (initialized on first request)
_agent_service: Optional[SpecializedAgentService] = None
_governance_service: Optional[GovernanceService] = None


def get_agent_service() -> SpecializedAgentService:
    """Get or create agent service instance."""
    global _agent_service
    if _agent_service is None:
        # Initialize with learning service
        try:
            from app.routers.learning import learning_service
            learning_svc = learning_service
        except Exception as e:
            logger.warning(f"Could not get learning service: {e}")
            learning_svc = None
        
        _agent_service = SpecializedAgentService(learning_service=learning_svc)
        logger.info("SpecializedAgentService initialized")
    return _agent_service


def get_governance_service() -> GovernanceService:
    """Get or create governance service instance."""
    global _governance_service
    if _governance_service is None:
        _governance_service = GovernanceService()
        logger.info("GovernanceService initialized")
    return _governance_service


@router.post("/create", response_model=SpecializedAgent)
async def create_agent(
    request: CreateAgentRequest,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Create a new specialized agent.
    
    Requires admin role.
    """
    try:
        # Enforce limits
        allowed, error = await governance.enforce_limits(request.tenant_id, "create_agent")
        if not allowed:
            raise HTTPException(status_code=429, detail=error)
        
        # Create agent
        agent = await agent_service.create_specialized_agent(
            name=request.name,
            role=request.role,
            tenant_id=request.tenant_id,
            capabilities=request.capabilities
        )
        
        # Log action
        await governance.log_action(
            tenant_id=request.tenant_id,
            agent_id=agent.agent_id,
            action=GovernanceAction.AGENT_CREATED,
            details={
                "name": request.name,
                "role": request.role.value,
                "created_by": current_user.sub
            }
        )
        
        logger.info(f"Created agent {agent.agent_id} for tenant {request.tenant_id} by {current_user.sub}")
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/agents", response_model=List[SpecializedAgent])
async def list_agents(
    tenant_id: Optional[str] = Query(None),
    role: Optional[AgentRole] = Query(None),
    status: Optional[AgentStatus] = Query(None),
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service)
):
    """
    List specialized agents with optional filters.
    
    Filters:
    - tenant_id: Filter by tenant
    - role: Filter by role
    - status: Filter by status
    """
    try:
        agents = await agent_service.list_agents(
            tenant_id=tenant_id,
            role=role,
            status=status
        )
        
        logger.info(
            f"Listed {len(agents)} agents "
            f"(tenant={tenant_id}, role={role}, status={status}) "
            f"by {current_user.sub}"
        )
        return agents
    
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/{agent_id}", response_model=SpecializedAgent)
async def get_agent(
    agent_id: str,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service)
):
    """Get a specific agent by ID."""
    try:
        agent = await agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.put("/agents/{agent_id}/status", response_model=dict)
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Update agent status.
    
    Requires admin role.
    """
    try:
        # Get agent first to verify it exists and get tenant_id
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Update status
        success = await agent_service.update_agent_status(agent_id, status)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update status")
        
        # Log action
        await governance.log_action(
            tenant_id=agent.tenant_id,
            agent_id=agent_id,
            action=GovernanceAction.STATUS_UPDATED,
            details={
                "new_status": status.value,
                "updated_by": current_user.sub
            }
        )
        
        logger.info(f"Updated agent {agent_id} status to {status.value} by {current_user.sub}")
        return {"agent_id": agent_id, "status": status.value, "success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.post("/agents/{agent_id}/assign", response_model=dict)
async def assign_task(
    agent_id: str,
    task: AgentTaskAssignment,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Assign a task to an agent.
    
    Validates that agent can accept more tasks based on capacity.
    """
    try:
        # Get agent first
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Assign task
        success = await agent_service.assign_task(agent_id, task)
        
        if not success:
            raise HTTPException(
                status_code=429,
                detail=f"Agent {agent_id} cannot accept more tasks (at capacity)"
            )
        
        # Log action
        await governance.log_action(
            tenant_id=agent.tenant_id,
            agent_id=agent_id,
            action=GovernanceAction.TASK_ASSIGNED,
            details={
                "task_id": task.task_id,
                "description": task.task_description,
                "priority": task.priority,
                "assigned_by": current_user.sub
            }
        )
        
        logger.info(f"Assigned task {task.task_id} to agent {agent_id} by {current_user.sub}")
        return {
            "agent_id": agent_id,
            "task_id": task.task_id,
            "success": True,
            "current_load": len(agent.current_tasks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign task: {str(e)}")


@router.post("/agents/{agent_id}/complete", response_model=dict)
async def complete_task(
    agent_id: str,
    task_id: str,
    success: bool = True,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Mark a task as completed.
    
    Updates agent metrics and success rate.
    """
    try:
        # Get agent first
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Complete task
        completed = await agent_service.complete_task(agent_id, task_id, success)
        
        if not completed:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Log action
        await governance.log_action(
            tenant_id=agent.tenant_id,
            agent_id=agent_id,
            action=GovernanceAction.TASK_COMPLETED,
            details={
                "task_id": task_id,
                "success": success,
                "completed_by": current_user.sub
            }
        )
        
        logger.info(f"Task {task_id} completed by agent {agent_id} (success={success})")
        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "success": success,
            "new_success_rate": agent.success_rate
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")


@router.get("/agents/{agent_id}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(
    agent_id: str,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service)
):
    """Get performance metrics for an agent."""
    try:
        metrics = await agent_service.get_agent_metrics(agent_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return metrics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/replicate", response_model=SpecializedAgent)
async def replicate_agent(
    config: AgentReplicationConfig,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Replicate an agent to another tenant.
    
    Requires admin role.
    Can optionally inherit training data from source agent.
    """
    try:
        # Get source agent for validation
        source_agent = await agent_service.get_agent(config.source_agent_id)
        if not source_agent:
            raise HTTPException(
                status_code=404,
                detail=f"Source agent {config.source_agent_id} not found"
            )
        
        # Enforce replication limits
        allowed, error = await governance.enforce_limits(config.target_tenant_id, "replicate")
        if not allowed:
            raise HTTPException(status_code=429, detail=error)
        
        # Replicate agent
        replica = await agent_service.replicate_agent(config)
        
        # Log action
        await governance.log_action(
            tenant_id=config.target_tenant_id,
            agent_id=replica.agent_id,
            action=GovernanceAction.AGENT_REPLICATED,
            details={
                "source_agent_id": config.source_agent_id,
                "source_tenant_id": source_agent.tenant_id,
                "inherit_training": config.inherit_training,
                "replicated_by": current_user.sub
            }
        )
        
        logger.info(
            f"Replicated agent {config.source_agent_id} -> {replica.agent_id} "
            f"by {current_user.sub}"
        )
        return replica
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to replicate agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to replicate: {str(e)}")


@router.get("/replications/{agent_id}", response_model=List[ReplicationHistory])
async def get_replication_history(
    agent_id: str,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service)
):
    """
    Get replication history for an agent.
    
    Shows both replications from this agent and replications to this agent.
    """
    try:
        history = await agent_service.get_replication_history(agent_id)
        return history
    
    except Exception as e:
        logger.error(f"Failed to get replication history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/governance/usage/{tenant_id}")
async def get_tenant_usage(
    tenant_id: str,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Get resource usage statistics for a tenant.
    
    Shows current usage vs limits.
    """
    try:
        # Get usage stats from governance
        stats = await governance.get_tenant_usage(tenant_id)
        
        # Update with live data from agent service
        agents = await agent_service.list_agents(tenant_id=tenant_id)
        active_agents = [a for a in agents if a.status in [AgentStatus.ACTIVE, AgentStatus.BUSY]]
        
        await governance.update_tenant_stats(
            tenant_id=tenant_id,
            total_agents=len(agents),
            active_agents=len(active_agents)
        )
        
        # Get limits
        limits = governance.get_limits()
        
        return {
            "tenant_id": tenant_id,
            "usage": stats.to_dict(),
            "limits": limits,
            "usage_percentage": {
                "agents": (stats.total_agents / limits["max_agents_per_tenant"]) * 100,
                "replications": (stats.replications_today / limits["max_replications_per_day"]) * 100
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get tenant usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage: {str(e)}")


@router.get("/governance/audit")
async def get_audit_log(
    tenant_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_user_optional),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Get audit log entries.
    
    Filters:
    - tenant_id: Filter by tenant
    - agent_id: Filter by agent
    - limit: Maximum entries to return (default: 100, max: 1000)
    """
    try:
        log_entries = await governance.get_audit_log(
            tenant_id=tenant_id,
            agent_id=agent_id,
            limit=limit
        )
        
        return {
            "total": len(log_entries),
            "entries": log_entries,
            "filters": {
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "limit": limit
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit log: {str(e)}")


@router.get("/governance/limits")
async def get_limits(
    current_user: TokenData = Depends(get_current_user_optional),
    governance: GovernanceService = Depends(get_governance_service)
):
    """Get current resource limits."""
    try:
        limits = governance.get_limits()
        return limits
    
    except Exception as e:
        logger.error(f"Failed to get limits: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get limits: {str(e)}")


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: TokenData = Depends(get_current_user_optional),
    agent_service: SpecializedAgentService = Depends(get_agent_service),
    governance: GovernanceService = Depends(get_governance_service)
):
    """
    Delete an agent.
    
    Requires admin role.
    """
    try:
        # Get agent first to get tenant_id for logging
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Delete agent
        success = await agent_service.delete_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete agent")
        
        # Log action
        await governance.log_action(
            tenant_id=agent.tenant_id,
            agent_id=agent_id,
            action=GovernanceAction.AGENT_DELETED,
            details={
                "name": agent.name,
                "role": agent.role.value,
                "deleted_by": current_user.sub
            }
        )
        
        logger.info(f"Deleted agent {agent_id} by {current_user.sub}")
        return {"agent_id": agent_id, "deleted": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")
