from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum


class SourceType(str, Enum):
    PDF = "pdf"
    URL = "url"
    TEXT = "text"
    ZIP = "zip"
    MARKDOWN = "markdown"


class RagSource(SQLModel, table=True):
    __tablename__ = "rag_sources"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    corpus_id: str = Field(index=True)
    source_type: SourceType
    name: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta: dict = Field(default={}, sa_column=Column(JSON))
    
    chunks: List["RagChunk"] = Relationship(back_populates="source")


class RagChunk(SQLModel, table=True):
    __tablename__ = "rag_chunks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="rag_sources.id", index=True)
    corpus_id: str = Field(index=True)
    text: str
    embedding: Optional[str] = None
    chunk_index: int = 0
    token_count: int = 0
    page_number: Optional[int] = None
    meta: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    source: Optional[RagSource] = Relationship(back_populates="chunks")


class AgentMemory(SQLModel, table=True):
    __tablename__ = "agent_memories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: str = Field(index=True)
    session_id: Optional[str] = Field(default=None, index=True)
    note: str
    is_pinned: bool = False
    importance: int = Field(default=5, ge=1, le=10)
    embedding: Optional[str] = None
    meta: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)


class TrainingJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingJob(SQLModel, table=True):
    __tablename__ = "training_jobs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True)
    agent_id: str = Field(index=True)
    corpus_id: str = Field(index=True)
    status: TrainingJobStatus = TrainingJobStatus.PENDING
    progress: float = 0.0
    total_chunks: int = 0
    processed_chunks: int = 0
    params: dict = Field(default={}, sa_column=Column(JSON))
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    eta_seconds: Optional[int] = None


class EvalDataset(SQLModel, table=True):
    __tablename__ = "eval_datasets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    item_count: int = 0
    created_by: str
    meta: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    items: List["EvalItem"] = Relationship(back_populates="dataset")
    runs: List["EvalRun"] = Relationship(back_populates="dataset")


class EvalItem(SQLModel, table=True):
    __tablename__ = "eval_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="eval_datasets.id", index=True)
    question: str
    expected_answer: str
    context: Optional[str] = None
    meta: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    dataset: Optional[EvalDataset] = Relationship(back_populates="items")


class EvalRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvalRun(SQLModel, table=True):
    __tablename__ = "eval_runs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(unique=True, index=True)
    dataset_id: int = Field(foreign_key="eval_datasets.id", index=True)
    agent_id: str = Field(index=True)
    status: EvalRunStatus = EvalRunStatus.PENDING
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    dataset: Optional[EvalDataset] = Relationship(back_populates="runs")
    metrics: List["EvalMetric"] = Relationship(back_populates="run")


class EvalMetric(SQLModel, table=True):
    __tablename__ = "eval_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="eval_runs.id", index=True)
    item_id: int = Field(foreign_key="eval_items.id")
    exact_match: float = 0.0
    semantic_similarity: float = 0.0
    latency_ms: int = 0
    actual_answer: str
    retrieval_score: Optional[float] = None
    context_used: Optional[str] = None
    meta: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    run: Optional[EvalRun] = Relationship(back_populates="metrics")
