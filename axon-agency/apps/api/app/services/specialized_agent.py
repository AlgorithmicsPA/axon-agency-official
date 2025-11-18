"""
Specialized Agent Service: Factory and management for specialized agents.

This service manages the lifecycle of specialized agents including:
- Agent creation with role-specific capabilities
- Task assignment and status tracking
- Performance metrics and success rates
- Multi-tenant isolation
- Agent replication across tenants
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import uuid

from app.models.meta_agent import (
    AgentRole,
    AgentStatus,
    AgentCapability,
    SpecializedAgent,
    AgentReplicationConfig,
    AgentMetrics,
    AgentTaskAssignment,
    ReplicationHistory
)
from app.services.learning import LearningService


class SpecializedAgentService:
    """
    Service for managing specialized agents.
    
    Current implementation:
    - In-memory storage with dict (MVP)
    - Multi-tenant isolation by tenant_id
    - Integration with LearningService for training data
    
    TODO: Persist to JSONL or DB for production
    """
    
    def __init__(self, learning_service: Optional[LearningService] = None):
        """Initialize specialized agent service."""
        self._agents: Dict[str, SpecializedAgent] = {}
        self._replication_history: List[ReplicationHistory] = []
        self.learning_service = learning_service
        logger.info("SpecializedAgentService initialized")
    
    def _default_capabilities_for_role(self, role: AgentRole) -> AgentCapability:
        """Get default capabilities for a given role."""
        capabilities_map = {
            AgentRole.SECURITY: AgentCapability(
                role=role,
                description="Security analysis, vulnerability detection, and penetration testing",
                specializations=[
                    "sql_injection",
                    "xss",
                    "csrf",
                    "auth_bypass",
                    "sensitive_data_exposure",
                    "security_misconfiguration"
                ],
                max_concurrent_tasks=5
            ),
            AgentRole.PERFORMANCE: AgentCapability(
                role=role,
                description="Performance profiling, optimization, and load testing",
                specializations=[
                    "cpu_profiling",
                    "memory_optimization",
                    "query_optimization",
                    "caching_strategies",
                    "load_testing",
                    "bottleneck_detection"
                ],
                max_concurrent_tasks=3
            ),
            AgentRole.QA: AgentCapability(
                role=role,
                description="Quality assurance, test generation, and bug detection",
                specializations=[
                    "unit_testing",
                    "integration_testing",
                    "e2e_testing",
                    "regression_testing",
                    "test_coverage_analysis",
                    "bug_reproduction"
                ],
                max_concurrent_tasks=7
            ),
            AgentRole.BUILDER: AgentCapability(
                role=role,
                description="Code generation, feature implementation, and refactoring",
                specializations=[
                    "api_development",
                    "frontend_components",
                    "database_schema",
                    "code_refactoring",
                    "architectural_patterns",
                    "dependency_management"
                ],
                max_concurrent_tasks=4
            ),
            AgentRole.PLANNER: AgentCapability(
                role=role,
                description="Architecture planning, task decomposition, and roadmap creation",
                specializations=[
                    "system_architecture",
                    "task_breakdown",
                    "dependency_analysis",
                    "timeline_estimation",
                    "risk_assessment",
                    "resource_allocation"
                ],
                max_concurrent_tasks=2
            ),
            AgentRole.TESTER: AgentCapability(
                role=role,
                description="Automated testing, test case design, and validation",
                specializations=[
                    "test_case_generation",
                    "boundary_testing",
                    "fuzzing",
                    "mutation_testing",
                    "snapshot_testing",
                    "visual_regression"
                ],
                max_concurrent_tasks=6
            )
        }
        
        return capabilities_map.get(role, AgentCapability(
            role=role,
            description=f"Specialized {role.value} agent",
            specializations=[],
            max_concurrent_tasks=5
        ))
    
    async def create_specialized_agent(
        self,
        name: str,
        role: AgentRole,
        tenant_id: str,
        capabilities: Optional[AgentCapability] = None
    ) -> SpecializedAgent:
        """
        Create a new specialized agent.
        
        Args:
            name: Agent name
            role: Agent role
            tenant_id: Tenant ID for multi-tenant isolation
            capabilities: Custom capabilities (uses defaults if None)
        
        Returns:
            Created agent
        """
        # Generate unique agent ID with tenant namespace
        agent_id = f"agent_{tenant_id}_{role.value}_{uuid.uuid4().hex[:8]}"
        
        # Use default capabilities if not provided
        if capabilities is None:
            capabilities = self._default_capabilities_for_role(role)
        
        # Create agent
        agent = SpecializedAgent(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            tenant_id=tenant_id,
            status=AgentStatus.IDLE,
            learning_data_path=f"agent_{tenant_id}_{agent_id}"
        )
        
        # Store agent
        self._agents[agent_id] = agent
        
        logger.info(f"Created specialized agent {agent_id} (role={role.value}, tenant={tenant_id})")
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[SpecializedAgent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent if found, None otherwise
        """
        return self._agents.get(agent_id)
    
    async def list_agents(
        self,
        tenant_id: Optional[str] = None,
        role: Optional[AgentRole] = None,
        status: Optional[AgentStatus] = None
    ) -> List[SpecializedAgent]:
        """
        List agents with optional filters.
        
        Args:
            tenant_id: Filter by tenant (multi-tenant isolation)
            role: Filter by role
            status: Filter by status
        
        Returns:
            List of matching agents
        """
        agents = list(self._agents.values())
        
        # Apply filters
        if tenant_id:
            agents = [a for a in agents if a.tenant_id == tenant_id]
        
        if role:
            agents = [a for a in agents if a.role == role]
        
        if status:
            agents = [a for a in agents if a.status == status]
        
        return agents
    
    async def assign_task(
        self,
        agent_id: str,
        task: AgentTaskAssignment
    ) -> bool:
        """
        Assign a task to a specialized agent.
        
        Args:
            agent_id: Target agent ID
            task: Task assignment details
        
        Returns:
            True if task assigned successfully, False otherwise
        """
        agent = self._agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        # Check if agent can accept more tasks
        current_load = len(agent.current_tasks)
        if current_load >= agent.capabilities.max_concurrent_tasks:
            logger.warning(
                f"Agent {agent_id} at capacity "
                f"({current_load}/{agent.capabilities.max_concurrent_tasks})"
            )
            return False
        
        # Assign task
        agent.current_tasks.append(task.task_id)
        agent.status = AgentStatus.BUSY
        agent.last_active = datetime.now()
        
        logger.info(
            f"Assigned task {task.task_id} to agent {agent_id} "
            f"(load={len(agent.current_tasks)}/{agent.capabilities.max_concurrent_tasks})"
        )
        
        return True
    
    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
        success: bool
    ) -> bool:
        """
        Mark a task as completed.
        
        Args:
            agent_id: Agent ID
            task_id: Task ID
            success: Whether task completed successfully
        
        Returns:
            True if task completed, False otherwise
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        
        # Remove task from current tasks
        if task_id in agent.current_tasks:
            agent.current_tasks.remove(task_id)
        
        # Update metrics
        agent.tasks_completed += 1
        # Update success rate (exponential moving average)
        alpha = 0.1  # Weight for new observation
        if success:
            agent.success_rate = (1 - alpha) * agent.success_rate + alpha * 1.0
        else:
            agent.success_rate = (1 - alpha) * agent.success_rate + alpha * 0.0
        
        # Update status
        if len(agent.current_tasks) == 0:
            agent.status = AgentStatus.IDLE
        
        agent.last_active = datetime.now()
        
        logger.info(
            f"Task {task_id} completed by agent {agent_id} "
            f"(success={success}, success_rate={agent.success_rate:.2f})"
        )
        
        return True
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus
    ) -> bool:
        """
        Update agent status.
        
        Args:
            agent_id: Agent ID
            status: New status
        
        Returns:
            True if updated, False otherwise
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        
        old_status = agent.status
        agent.status = status
        agent.last_active = datetime.now()
        
        logger.info(f"Agent {agent_id} status: {old_status.value} -> {status.value}")
        return True
    
    async def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """
        Get performance metrics for an agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent metrics if found, None otherwise
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        
        # Calculate uptime
        uptime_hours = (datetime.now() - agent.created_at).total_seconds() / 3600
        
        # Calculate failed tasks (approximation)
        tasks_failed = int(agent.tasks_completed * (1 - agent.success_rate))
        
        return AgentMetrics(
            agent_id=agent_id,
            tasks_completed=agent.tasks_completed,
            tasks_failed=tasks_failed,
            success_rate=agent.success_rate,
            current_load=len(agent.current_tasks),
            max_concurrent_tasks=agent.capabilities.max_concurrent_tasks,
            uptime_hours=uptime_hours,
            last_active=agent.last_active
        )
    
    async def replicate_agent(
        self,
        config: AgentReplicationConfig
    ) -> SpecializedAgent:
        """
        Replicate an agent to another tenant.
        
        Args:
            config: Replication configuration
        
        Returns:
            Newly created agent replica
        
        Raises:
            ValueError: If source agent not found
        """
        # Get source agent
        source_agent = self._agents.get(config.source_agent_id)
        if not source_agent:
            raise ValueError(f"Source agent {config.source_agent_id} not found")
        
        # Create replica with new ID
        replica_name = config.new_name or f"{source_agent.name} (Replica)"
        replica_capabilities = config.custom_capabilities or source_agent.capabilities
        
        replica = await self.create_specialized_agent(
            name=replica_name,
            role=source_agent.role,
            tenant_id=config.target_tenant_id,
            capabilities=replica_capabilities
        )
        
        # Copy training data if requested
        outcomes_copied = 0
        if config.inherit_training and self.learning_service:
            outcomes_copied = await self._copy_training_data(
                source_agent.agent_id,
                replica.agent_id
            )
        
        # Record replication history
        replication_record = ReplicationHistory(
            replication_id=f"repl_{uuid.uuid4().hex[:8]}",
            source_agent_id=source_agent.agent_id,
            target_agent_id=replica.agent_id,
            source_tenant_id=source_agent.tenant_id,
            target_tenant_id=config.target_tenant_id,
            replicated_at=datetime.now(),
            training_inherited=config.inherit_training,
            outcomes_copied=outcomes_copied
        )
        self._replication_history.append(replication_record)
        
        logger.info(
            f"Replicated agent {source_agent.agent_id} -> {replica.agent_id} "
            f"(tenant: {source_agent.tenant_id} -> {config.target_tenant_id}, "
            f"outcomes_copied={outcomes_copied})"
        )
        
        return replica
    
    async def _copy_training_data(
        self,
        source_id: str,
        target_id: str
    ) -> int:
        """
        Copy training data from source agent to target agent.
        
        Args:
            source_id: Source agent ID
            target_id: Target agent ID
        
        Returns:
            Number of outcomes copied
        """
        if not self.learning_service:
            logger.warning("LearningService not available, skipping training data copy")
            return 0
        
        # Get source agent's outcomes
        # Note: This is a simplified implementation
        # In production, we'd filter outcomes by agent namespace
        source_agent = self._agents.get(source_id)
        target_agent = self._agents.get(target_id)
        
        if not source_agent or not target_agent:
            return 0
        
        # For MVP, we just log the intent
        # TODO: Implement actual outcome filtering and copying in LearningService
        logger.info(
            f"Would copy training data from {source_id} to {target_id} "
            f"(namespace: {source_agent.learning_data_path} -> {target_agent.learning_data_path})"
        )
        
        # Simulated copy count
        return 0
    
    async def get_replication_history(
        self,
        agent_id: Optional[str] = None
    ) -> List[ReplicationHistory]:
        """
        Get replication history.
        
        Args:
            agent_id: Filter by source or target agent ID (optional)
        
        Returns:
            List of replication records
        """
        if not agent_id:
            return self._replication_history
        
        return [
            r for r in self._replication_history
            if r.source_agent_id == agent_id or r.target_agent_id == agent_id
        ]
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            True if deleted, False if not found
        """
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            del self._agents[agent_id]
            logger.info(f"Deleted agent {agent_id} (tenant={agent.tenant_id})")
            return True
        return False
