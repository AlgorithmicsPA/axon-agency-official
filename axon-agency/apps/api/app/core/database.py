"""Database configuration and session management."""

from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

from app.models.rag import (
    RagSource, RagChunk, AgentMemory,
    TrainingJob, EvalDataset, EvalItem, EvalRun, EvalMetric
)
from app.models.orders import Order

_engine = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        _engine = create_engine(
            settings.database_url,
            echo=False,
            connect_args=connect_args,
            pool_pre_ping=True if not settings.database_url.startswith("sqlite") else False
        )
    return _engine


def create_db_and_tables():
    """Create database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
