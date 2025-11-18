import json
import os
import re
from typing import Optional
from loguru import logger
from app.core.types import DetectedServices


def load_audit_file(path: str = "axon88_audit.json") -> Optional[dict]:
    """Load axon88_audit.json if available."""
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        logger.warning(f"Audit file not found: {path}")
        return None
    except Exception as e:
        logger.error(f"Failed to load audit file: {e}")
        return None


def detect_services_from_audit(audit_data: Optional[dict]) -> DetectedServices:
    """Detect services and ports from audit data."""
    detected = DetectedServices()
    
    if not audit_data:
        return detected
    
    try:
        endpoints = audit_data.get("ENDPOINTS_AND_APIS", "")
        
        if ":11434" in endpoints:
            detected.ollama = 11434
        
        if ":5679" in endpoints or "n8n" in audit_data.get("containers", ""):
            detected.n8n = 5679
        
        if ":80 " in endpoints or "nginx" in audit_data.get("services_and_commands", ""):
            detected.nginx = 80
        
        if ":5432" in endpoints or "postgres" in audit_data.get("containers", ""):
            detected.postgres = 5432
        
        fastapi_ports = []
        for port in [8091, 8089, 8000, 8080]:
            if f":{port}" in endpoints:
                fastapi_ports.append(port)
        if fastapi_ports:
            detected.fastapi = fastapi_ports
        
        if ":20241" in endpoints or "cloudflared" in audit_data.get("services_and_commands", ""):
            detected.cloudflared = 20241
        
        if ":3389" in endpoints:
            detected.xrdp = 3389
        
        if ":22 " in endpoints or ":22\n" in endpoints:
            detected.ssh = 22
        
        containers = audit_data.get("containers", "")
        if "Docker version" in containers:
            detected.docker = True
        
        services = audit_data.get("services_and_commands", "")
        if "systemd" in services.lower() or ".service" in services:
            detected.systemd = True
        
        nvidia = audit_data.get("system_nvidia", "")
        if "CUDA" in nvidia or "nvidia" in nvidia.lower():
            detected.cuda = True
        
    except Exception as e:
        logger.error(f"Error detecting services: {e}")
    
    return detected


def get_system_capabilities(detected: DetectedServices) -> dict[str, bool]:
    """Determine system capabilities based on detected services."""
    return {
        "llm_local": detected.ollama is not None,
        "llm_cloud": True,
        "workflows": detected.n8n is not None,
        "containers": detected.docker,
        "systemd": detected.systemd,
        "gpu": detected.cuda,
        "tunnels": detected.cloudflared is not None,
        "database": detected.postgres is not None,
        "web_server": detected.nginx is not None,
    }
