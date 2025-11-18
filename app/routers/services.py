from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload, ServiceInfo, ServiceType
from app.core.utils import write_audit_log
from app.config import settings
from app.security import require_admin
from app.adapters.services_systemd import SystemdAdapter
from app.adapters.services_docker import DockerAdapter
from loguru import logger


router = APIRouter(prefix="/api", tags=["services"])


class ListServicesRequest(BaseModel):
    type: ServiceType | None = None


class ListServicesResponse(BaseModel):
    services: List[ServiceInfo]


class ServiceActionRequest(BaseModel):
    service_name: str
    service_type: ServiceType
    action: str


@router.post("/services/list", response_model=ListServicesResponse)
async def list_services(
    request: ListServicesRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """List available services."""
    services = []
    
    if request.type is None or request.type == ServiceType.SYSTEMD:
        systemd_adapter = SystemdAdapter()
        try:
            systemd_services = await systemd_adapter.list_services()
            services.extend(systemd_services)
        except Exception as e:
            logger.warning(f"Failed to list systemd services: {e}")
    
    if request.type is None or request.type == ServiceType.DOCKER:
        docker_adapter = DockerAdapter()
        try:
            docker_services = await docker_adapter.list_containers()
            services.extend(docker_services)
        except Exception as e:
            logger.warning(f"Failed to list docker containers: {e}")
    
    return ListServicesResponse(services=services)


@router.post("/services/action")
async def service_action(
    request: ServiceActionRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Execute action on a service (start, stop, restart)."""
    require_admin(current_user)
    
    if request.action not in ["start", "stop", "restart", "status"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        if request.service_type == ServiceType.SYSTEMD:
            adapter = SystemdAdapter()
            result = await adapter.service_action(request.service_name, request.action)
        elif request.service_type == ServiceType.DOCKER:
            adapter = DockerAdapter()
            result = await adapter.container_action(request.service_name, request.action)
        else:
            raise HTTPException(status_code=400, detail="Invalid service type")
        
        write_audit_log(
            "service_action",
            current_user.sub,
            {"service": request.service_name, "type": request.service_type, "action": request.action},
            settings.audit_log_path,
        )
        
        return {"message": f"Action {request.action} executed", "result": result}
        
    except Exception as e:
        logger.error(f"Service action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
