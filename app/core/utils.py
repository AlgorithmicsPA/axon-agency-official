import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from loguru import logger


def safe_path_join(base: str, *paths: str) -> Path:
    """Safely join paths and prevent path traversal attacks."""
    base_path = Path(base).resolve()
    target_path = Path(base, *paths).resolve()
    
    if not str(target_path).startswith(str(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")
    
    return target_path


def is_command_allowed(cmd: str, allowed_commands: list[str]) -> bool:
    """Check if a command is in the whitelist."""
    if not cmd:
        return False
    
    cmd_parts = cmd.strip().split()
    if not cmd_parts:
        return False
    
    cmd_executable = cmd_parts[0]
    
    return cmd_executable in allowed_commands


def sanitize_command(cmd: str) -> str:
    """Basic command sanitization."""
    dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">"]
    
    for char in dangerous_chars:
        if char in cmd:
            raise ValueError(f"Dangerous character detected in command: {char}")
    
    return cmd.strip()


def write_audit_log(event_type: str, user: str, data: Dict[str, Any], log_path: str):
    """Write audit log entry."""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "user": user,
            "data": data
        }
        
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "< 1m"


def parse_size_string(size_str: str) -> int:
    """Parse size strings like '10MB' to bytes."""
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4
    }
    
    size_str = size_str.upper().strip()
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
            except ValueError:
                return 10 * 1024 * 1024
    
    return 10 * 1024 * 1024
