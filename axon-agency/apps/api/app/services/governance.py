"""
Governance Service: Resource limits and audit logging for meta-agent system.

This service enforces governance policies including:
- Resource limits per tenant (max agents, tasks, replications)
- Audit logging for all meta-agent actions
- Usage statistics and reporting
- Multi-tenant quota management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger
import json
from enum import Enum


class GovernanceAction(str, Enum):
    """Governance audit action types."""
    AGENT_CREATED = "agent_created"
    AGENT_DELETED = "agent_deleted"
    AGENT_REPLICATED = "agent_replicated"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    STATUS_UPDATED = "status_updated"
    LIMIT_EXCEEDED = "limit_exceeded"


class AuditLogEntry:
    """Audit log entry."""
    
    def __init__(
        self,
        tenant_id: str,
        agent_id: Optional[str],
        action: GovernanceAction,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.action = action
        self.details = details
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "action": self.action.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        """Create from dictionary."""
        return cls(
            tenant_id=data["tenant_id"],
            agent_id=data.get("agent_id"),
            action=GovernanceAction(data["action"]),
            details=data["details"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class TenantUsageStats:
    """Tenant usage statistics."""
    
    def __init__(
        self,
        tenant_id: str,
        total_agents: int = 0,
        active_agents: int = 0,
        total_tasks: int = 0,
        tasks_completed: int = 0,
        replications_today: int = 0,
        replications_total: int = 0
    ):
        self.tenant_id = tenant_id
        self.total_agents = total_agents
        self.active_agents = active_agents
        self.total_tasks = total_tasks
        self.tasks_completed = tasks_completed
        self.replications_today = replications_today
        self.replications_total = replications_total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "total_agents": self.total_agents,
            "active_agents": self.active_agents,
            "total_tasks": self.total_tasks,
            "tasks_completed": self.tasks_completed,
            "replications_today": self.replications_today,
            "replications_total": self.replications_total
        }


class GovernanceService:
    """
    Service for governance, limits, and audit logging.
    
    Enforces resource limits:
    - Max agents per tenant
    - Max concurrent tasks per agent
    - Max replications per day
    
    Provides audit trail for all meta-agent actions.
    """
    
    def __init__(
        self,
        storage_path: str = "storage/governance",
        max_agents_per_tenant: int = 10,
        max_concurrent_tasks_per_agent: int = 5,
        max_replications_per_day: int = 3
    ):
        """Initialize governance service."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.audit_log_file = self.storage_path / "audit.jsonl"
        self.audit_log: List[AuditLogEntry] = []
        
        # Resource limits
        self.max_agents_per_tenant = max_agents_per_tenant
        self.max_concurrent_tasks_per_agent = max_concurrent_tasks_per_agent
        self.max_replications_per_day = max_replications_per_day
        
        # In-memory usage tracking
        self._tenant_stats: Dict[str, TenantUsageStats] = {}
        
        # Load historical audit log
        self._load_audit_log()
        
        logger.info(
            f"GovernanceService initialized with limits: "
            f"agents={max_agents_per_tenant}, "
            f"tasks={max_concurrent_tasks_per_agent}, "
            f"replications/day={max_replications_per_day}"
        )
    
    def _load_audit_log(self):
        """Load historical audit log from disk."""
        if not self.audit_log_file.exists():
            return
        
        try:
            with open(self.audit_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.audit_log.append(AuditLogEntry.from_dict(data))
            logger.info(f"Loaded {len(self.audit_log)} audit log entries")
        except Exception as e:
            logger.error(f"Failed to load audit log: {e}")
    
    def _save_audit_entry(self, entry: AuditLogEntry):
        """Append audit entry to JSONL file."""
        try:
            with open(self.audit_log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to save audit entry: {e}")
    
    async def log_action(
        self,
        tenant_id: str,
        agent_id: Optional[str],
        action: GovernanceAction,
        details: Dict[str, Any]
    ):
        """
        Log an action to the audit trail.
        
        Args:
            tenant_id: Tenant ID
            agent_id: Agent ID (optional)
            action: Action type
            details: Additional details
        """
        entry = AuditLogEntry(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action=action,
            details=details
        )
        
        self.audit_log.append(entry)
        self._save_audit_entry(entry)
        
        # CRITICAL FIX: Invalidate cache for this tenant to ensure fresh stats
        if tenant_id in self._tenant_stats:
            del self._tenant_stats[tenant_id]
        
        logger.debug(
            f"Audit: {action.value} by tenant={tenant_id} agent={agent_id}"
        )
    
    async def enforce_limits(
        self,
        tenant_id: str,
        action: str,
        current_count: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Enforce resource limits before action.
        
        Args:
            tenant_id: Tenant ID
            action: Action type (create_agent, replicate, assign_task)
            current_count: Current count of resources (optional)
        
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        if action == "create_agent":
            stats = await self.get_tenant_usage(tenant_id)
            if stats.total_agents >= self.max_agents_per_tenant:
                error = (
                    f"Tenant {tenant_id} has reached max agents limit "
                    f"({self.max_agents_per_tenant})"
                )
                await self.log_action(
                    tenant_id=tenant_id,
                    agent_id=None,
                    action=GovernanceAction.LIMIT_EXCEEDED,
                    details={"limit": "max_agents_per_tenant", "value": self.max_agents_per_tenant}
                )
                return False, error
        
        elif action == "replicate":
            stats = await self.get_tenant_usage(tenant_id)
            if stats.replications_today >= self.max_replications_per_day:
                error = (
                    f"Tenant {tenant_id} has reached max replications/day limit "
                    f"({self.max_replications_per_day})"
                )
                await self.log_action(
                    tenant_id=tenant_id,
                    agent_id=None,
                    action=GovernanceAction.LIMIT_EXCEEDED,
                    details={"limit": "max_replications_per_day", "value": self.max_replications_per_day}
                )
                return False, error
        
        elif action == "assign_task":
            if current_count is not None and current_count >= self.max_concurrent_tasks_per_agent:
                error = (
                    f"Agent has reached max concurrent tasks limit "
                    f"({self.max_concurrent_tasks_per_agent})"
                )
                return False, error
        
        return True, None
    
    async def get_audit_log(
        self,
        tenant_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            tenant_id: Filter by tenant ID (optional)
            agent_id: Filter by agent ID (optional)
            limit: Maximum entries to return
        
        Returns:
            List of audit log entries (most recent first)
        """
        entries = self.audit_log
        
        # Apply filters
        if tenant_id:
            entries = [e for e in entries if e.tenant_id == tenant_id]
        
        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        
        # Sort by timestamp (most recent first) and limit
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]
        
        return [e.to_dict() for e in entries]
    
    async def get_tenant_usage(self, tenant_id: str) -> TenantUsageStats:
        """
        Get usage statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            Tenant usage statistics
        """
        # Check cache
        if tenant_id in self._tenant_stats:
            return self._tenant_stats[tenant_id]
        
        # Calculate from audit log
        stats = TenantUsageStats(tenant_id=tenant_id)
        
        # Get today's date for replications
        today = datetime.now().date()
        
        for entry in self.audit_log:
            if entry.tenant_id != tenant_id:
                continue
            
            if entry.action == GovernanceAction.AGENT_CREATED:
                stats.total_agents += 1
            elif entry.action == GovernanceAction.AGENT_DELETED:
                stats.total_agents = max(0, stats.total_agents - 1)
            elif entry.action == GovernanceAction.TASK_ASSIGNED:
                stats.total_tasks += 1
            elif entry.action == GovernanceAction.TASK_COMPLETED:
                stats.tasks_completed += 1
            elif entry.action == GovernanceAction.AGENT_REPLICATED:
                stats.replications_total += 1
                if entry.timestamp.date() == today:
                    stats.replications_today += 1
        
        # Cache stats
        self._tenant_stats[tenant_id] = stats
        
        return stats
    
    async def update_tenant_stats(
        self,
        tenant_id: str,
        total_agents: Optional[int] = None,
        active_agents: Optional[int] = None
    ):
        """
        Update tenant statistics (called by SpecializedAgentService).
        
        Args:
            tenant_id: Tenant ID
            total_agents: Total agents count
            active_agents: Active agents count
        """
        stats = await self.get_tenant_usage(tenant_id)
        
        if total_agents is not None:
            stats.total_agents = total_agents
        if active_agents is not None:
            stats.active_agents = active_agents
        
        self._tenant_stats[tenant_id] = stats
    
    def get_limits(self) -> Dict[str, int]:
        """
        Get current resource limits.
        
        Returns:
            Dictionary of limits
        """
        return {
            "max_agents_per_tenant": self.max_agents_per_tenant,
            "max_concurrent_tasks_per_agent": self.max_concurrent_tasks_per_agent,
            "max_replications_per_day": self.max_replications_per_day
        }
    
    async def clear_cache(self):
        """Clear cached tenant statistics (for testing)."""
        self._tenant_stats.clear()
        logger.info("Cleared governance cache")
