from datetime import datetime
from typing import Optional, Literal, Any
from sqlmodel import SQLModel, Field, Column, JSON, String
from pydantic import BaseModel
from enum import Enum


class ImprovementType(str, Enum):
    REFACTOR_COMPLEXITY = "refactor_complexity"
    SPLIT_LARGE_FILE = "split_large_file"
    REDUCE_COUPLING = "reduce_coupling"
    ADD_DOCUMENTATION = "add_documentation"
    OPTIMIZE_IMPORTS = "optimize_imports"
    FIX_CODE_SMELL = "fix_code_smell"
    ADD_TESTS = "add_tests"
    UPGRADE_DEPENDENCY = "upgrade_dependency"


class ImprovementJobStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ImprovementJob(SQLModel, table=True):
    __tablename__ = "improvement_jobs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True)
    
    improvement_type: ImprovementType
    target_file: str = Field(index=True)
    
    title: str
    description: str = Field(sa_column=Column(String))
    rationale: Optional[str] = None
    
    diff_preview: Optional[str] = Field(default=None, sa_column=Column(String))
    success_criteria: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    status: ImprovementJobStatus = ImprovementJobStatus.PENDING
    priority: int = Field(default=5, ge=1, le=10)
    
    before_metrics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    after_metrics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    error_message: Optional[str] = None
    
    worktree_path: Optional[str] = None
    
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ImprovementProposal(BaseModel):
    """
    Proposal from autonomous agent for code improvement.
    Sent to Architect for review before applying changes.
    """
    session_id: str
    iteration: int
    files: list[str]
    diff: str
    summary: str
    reason: str
    before_metrics: Optional[dict] = None
    predicted_success: Optional[float] = None


class ArchitectDecision(BaseModel):
    """
    Decision from Architect Agent after reviewing improvement proposal.
    """
    decision: Literal["approve", "revise", "reject"]
    risk_level: Literal["low", "medium", "high"]
    confidence: float
    comments: str
    required_changes: list[str] = []


class ReviewerDecision(BaseModel):
    """Decision from a specialized reviewer."""
    reviewer_name: str
    decision: Literal["approve", "revise", "reject"]
    risk_level: Literal["low", "medium", "high"]
    confidence: float
    comments: str
    concerns: list[str] = []
    recommendations: list[str] = []


class CouncilDecision(BaseModel):
    """
    Aggregated decision from the Review Council.
    
    The Review Council runs BEFORE the Architect Supervisor in the review flow.
    Therefore, architect_decision will always be None at the time of council review.
    
    Consumers should use both council_decision and architect_decision separately
    from the improvement result dict, not rely on this field.
    
    Flow: Council Review → AutonomousAgent → Architect Review
    Result: {council_decision: CouncilDecision, architect_decision: ArchitectDecision}
    """
    final_decision: Literal["approve", "revise", "reject"]
    overall_risk_level: Literal["low", "medium", "high"]
    overall_confidence: float
    summary: str
    architect_decision: Optional[ArchitectDecision] = None  # Always None (Council runs before Architect)
    security_decision: Optional[ReviewerDecision] = None
    performance_decision: Optional[ReviewerDecision] = None
    qa_decision: Optional[ReviewerDecision] = None
    voting_breakdown: dict[str, Any] = {}
