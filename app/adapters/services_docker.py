import docker
from typing import List
from app.core.types import ServiceInfo, ServiceType, ServiceStatus
from loguru import logger


class DockerAdapter:
    """Adapter for Docker container management."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker not available (Replit/degraded mode): {e}")
            self.client = None
    
    async def list_containers(self, all_containers: bool = True) -> List[ServiceInfo]:
        """List Docker containers."""
        if not self.client:
            return []
        
        try:
            containers = self.client.containers.list(all=all_containers)
            
            services = []
            for container in containers:
                status_map = {
                    "running": ServiceStatus.ACTIVE,
                    "exited": ServiceStatus.INACTIVE,
                    "paused": ServiceStatus.INACTIVE,
                    "dead": ServiceStatus.FAILED,
                }
                
                status = status_map.get(container.status, ServiceStatus.UNKNOWN)
                
                services.append(ServiceInfo(
                    name=container.name,
                    type=ServiceType.DOCKER,
                    status=status,
                    description=container.image.tags[0] if container.image.tags else None,
                    metadata={
                        "id": container.short_id,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "status": container.status,
                    }
                ))
            
            return services
            
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []
    
    async def container_action(self, container_name: str, action: str) -> dict:
        """Execute action on Docker container."""
        if not self.client:
            raise Exception("Docker not available")
        
        try:
            container = self.client.containers.get(container_name)
            
            if action == "start":
                container.start()
            elif action == "stop":
                container.stop()
            elif action == "restart":
                container.restart()
            elif action == "status":
                container.reload()
            else:
                raise ValueError(f"Invalid action: {action}")
            
            container.reload()
            
            return {
                "success": True,
                "status": container.status,
                "id": container.short_id,
            }
            
        except Exception as e:
            logger.error(f"Container action error: {e}")
            raise Exception(f"Failed to execute action: {str(e)}")
