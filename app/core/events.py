from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel


class EventType(str, Enum):
    COMMAND_STARTED = "command_started"
    COMMAND_OUTPUT = "command_output"
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
    SERVICE_STATUS_CHANGED = "service_status_changed"
    METRICS_UPDATE = "metrics_update"
    SYSTEM_ALERT = "system_alert"


class Event(BaseModel):
    event_type: EventType
    data: Dict[str, Any]
    timestamp: str
