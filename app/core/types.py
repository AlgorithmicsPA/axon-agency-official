from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Role(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"


class TokenPayload(BaseModel):
    sub: str
    role: Role
    iss: str
    aud: str
    exp: int
    iat: int


class ServiceType(str, Enum):
    SYSTEMD = "systemd"
    DOCKER = "docker"


class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ServiceInfo(BaseModel):
    name: str
    type: ServiceType
    status: ServiceStatus
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CommandStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CommandTask(BaseModel):
    task_id: str
    cmd: str
    status: CommandStatus
    exit_code: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    SDXL = "sdxl"


class LLMInputKind(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TEXT_AND_IMAGE = "text_and_image"


class LLMInput(BaseModel):
    kind: LLMInputKind
    prompt: str
    image_url: Optional[str] = None
    image_base64: Optional[str] = None


class LLMResponse(BaseModel):
    provider: LLMProvider
    model: str
    output: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricsSnapshot(BaseModel):
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    disk_free_gb: float
    uptime_seconds: float
    gpu_utilization: Optional[float] = None
    gpu_temp: Optional[float] = None
    load_average: Optional[List[float]] = None


class DetectedServices(BaseModel):
    ollama: Optional[int] = None
    n8n: Optional[int] = None
    nginx: Optional[int] = None
    postgres: Optional[int] = None
    fastapi: Optional[List[int]] = None
    docker: bool = False
    cloudflared: Optional[int] = None
    xrdp: Optional[int] = None
    ssh: Optional[int] = None
    systemd: bool = False
    cuda: bool = False


class CatalogResponse(BaseModel):
    version: str
    dev_mode: bool
    audit_loaded: bool
    services_detected: DetectedServices
    capabilities: Dict[str, bool]
