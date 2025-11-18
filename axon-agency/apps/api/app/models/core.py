"""SQLModel database models for AXON Agency."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, String, JSON
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    VIEWER = "viewer"
    MEMBER = "member"


class CampaignStatus(str, Enum):
    """Campaign execution status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class PostStatus(str, Enum):
    """Post publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class User(SQLModel, table=True):
    """User account."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    role: str = Field(default=UserRole.VIEWER.value)
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    tenant_id: Optional[str] = Field(
        default=None,
        foreign_key="tenants.id",
        description="If set, this user belongs to a specific tenant workspace"
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Team(SQLModel, table=True):
    """Team/Organization."""
    __tablename__ = "teams"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Partner(SQLModel, table=True):
    """Business partner."""
    __tablename__ = "partners"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    company: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Membership(SQLModel, table=True):
    """User membership/subscription."""
    __tablename__ = "memberships"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    plan_name: str
    status: str = Field(default="active")
    starts_at: datetime
    expires_at: Optional[datetime] = None
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(SQLModel, table=True):
    """Marketing/automation campaign."""
    __tablename__ = "campaigns"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    goal: str
    status: str = Field(default=CampaignStatus.DRAFT.value, index=True)
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    results: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: int = Field(foreign_key="users.id")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    """Content post/landing page."""
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    topic: str
    brief: Optional[str] = None
    content: str = Field(default="", sa_column=Column(String))
    status: str = Field(default=PostStatus.DRAFT.value, index=True)
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: int = Field(foreign_key="users.id")
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Media(SQLModel, table=True):
    """Media file (images, videos, documents)."""
    __tablename__ = "media"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    url: str
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    uploaded_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Chat conversation log."""
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: str
    content: str = Field(sa_column=Column(String))
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Autopilot(SQLModel, table=True):
    """Registered autopilot/agent."""
    __tablename__ = "autopilots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    last_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsEvent(SQLModel, table=True):
    """Analytics event tracking."""
    __tablename__ = "analytics_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    session_id: Optional[str] = Field(index=True)
    page_url: Optional[str] = None
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Comment(SQLModel, table=True):
    """User feedback/comments."""
    __tablename__ = "comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(String))
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    post_id: Optional[int] = Field(default=None, foreign_key="posts.id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    is_approved: bool = Field(default=False)
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
