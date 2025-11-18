"""Services management stub endpoints."""

import logging
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list")
async def list_services(current_user = Depends(get_current_user)):
    """List system services (stub)."""
    return {
        "services": [
            {"name": "api", "status": "running"},
            {"name": "database", "status": "running"},
            {"name": "redis", "status": "unknown"}
        ]
    }


@router.post("/{service_name}/control")
async def control_service(
    service_name: str,
    action: str,
    current_user = Depends(get_current_user)
):
    """Control service (stub)."""
    logger.info(f"Service control: {service_name} - {action}")
    return {"service": service_name, "action": action, "status": "ok"}
