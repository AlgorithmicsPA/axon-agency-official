"""
Meta-Agent Models: Specialized agent roles, capabilities, and replication.

This module defines the data models for FASE 8 - Meta-Agent system that enables:
- Specialized agent roles (SECURITY, PERFORMANCE, QA, BUILDER, PLANNER, TESTER)
- Agent capabilities and configurations
- Multi-tenant agent management with isolation
- Agent replication across tenants with learning inheritance
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Specialized agent roles."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    QA = "qa"
    BUILDER = "builder"
    PLANNER = "planner"
    TESTER = "tester"


class AgentStatus(str, Enum):
    """Agent operational status."""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    DISABLED = "disabled"
    REPLICATING = "replicating"


class AgentCapability(BaseModel):
    """Agent capability definition."""
    role: AgentRole
    description: str
    specializations: List[str] = Field(default_factory=list)
    max_concurrent_tasks: int = Field(default=5, ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "security",
                "description": "Security analysis and vulnerability detection",
                "specializations": ["sql_injection", "xss", "auth_bypass"],
                "max_concurrent_tasks": 5
            }
        }


class SpecializedAgent(BaseModel):
    """Specialized agent instance."""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: AgentCapability
    tenant_id: str
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    tasks_completed: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    learning_data_path: Optional[str] = None
    current_tasks: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_tenant1_sec_001",
                "name": "Security Specialist Alpha",
                "role": "security",
                "capabilities": {
                    "role": "security",
                    "description": "Security analysis and vulnerability detection",
                    "specializations": ["sql_injection", "xss", "auth_bypass"],
                    "max_concurrent_tasks": 5
                },
                "tenant_id": "tenant1",
                "status": "idle",
                "tasks_completed": 42,
                "success_rate": 0.95
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities.model_dump(),
            "tenant_id": self.tenant_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
            "learning_data_path": self.learning_data_path,
            "current_tasks": self.current_tasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpecializedAgent":
        """Create from dictionary."""
        data["role"] = AgentRole(data["role"])
        data["status"] = AgentStatus(data["status"])
        data["capabilities"] = AgentCapability(**data["capabilities"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("last_active"):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)


class AgentReplicationConfig(BaseModel):
    """Configuration for agent replication."""
    source_agent_id: str
    target_tenant_id: str
    inherit_training: bool = Field(default=True)
    custom_capabilities: Optional[AgentCapability] = None
    new_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_agent_id": "agent_tenant1_sec_001",
                "target_tenant_id": "tenant2",
                "inherit_training": True,
                "new_name": "Security Specialist Beta"
            }
        }


class AgentTaskAssignment(BaseModel):
    """Task assignment request."""
    task_id: str
    task_description: str
    priority: int = Field(default=5, ge=1, le=10)
    estimated_duration_minutes: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_001",
                "task_description": "Analyze authentication flow for vulnerabilities",
                "priority": 8,
                "estimated_duration_minutes": 30
            }
        }


class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    avg_task_duration_minutes: Optional[float] = None
    current_load: int
    max_concurrent_tasks: int
    uptime_hours: float
    last_active: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_tenant1_sec_001",
                "tasks_completed": 42,
                "tasks_failed": 2,
                "success_rate": 0.95,
                "avg_task_duration_minutes": 15.5,
                "current_load": 2,
                "max_concurrent_tasks": 5,
                "uptime_hours": 168.5,
                "last_active": "2025-11-13T10:30:00"
            }
        }


class ReplicationHistory(BaseModel):
    """Record of agent replication."""
    replication_id: str
    source_agent_id: str
    target_agent_id: str
    source_tenant_id: str
    target_tenant_id: str
    replicated_at: datetime
    training_inherited: bool
    outcomes_copied: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "replication_id": "repl_001",
                "source_agent_id": "agent_tenant1_sec_001",
                "target_agent_id": "agent_tenant2_sec_001",
                "source_tenant_id": "tenant1",
                "target_tenant_id": "tenant2",
                "replicated_at": "2025-11-13T10:30:00",
                "training_inherited": True,
                "outcomes_copied": 150
            }
        }
