"""LLM Router models and enums."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TaskType(str, Enum):
    """Types of tasks that can be routed to different LLM providers."""
    SIMPLE_TEXT = "simple_text"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    COMPLEX_REASONING = "complex_reasoning"
    IMAGE_GENERATION = "image_generation"


class LLMResponse(BaseModel):
    """Response from LLM router execution."""
    model_config = ConfigDict(protected_namespaces=())
    
    provider: str
    content: str
    tokens_used: int = 0
    latency_ms: float
    fallback_used: bool = False
    task_type: TaskType
    model_used: Optional[str] = None


class ProviderStatus(BaseModel):
    """Status and health metrics for an LLM provider."""
    provider: str
    available: bool
    latency_avg: float = 0.0
    success_rate: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
