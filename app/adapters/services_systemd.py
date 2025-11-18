import subprocess
import asyncio
from typing import List
from app.core.types import ServiceInfo, ServiceType, ServiceStatus
from loguru import logger


class SystemdAdapter:
    """Adapter for systemd service management."""
    
    async def list_services(self, pattern: str = "*.service") -> List[ServiceInfo]:
        """List systemd services."""
        try:
            result = await asyncio.create_subprocess_exec(
                "systemctl", "list-units", "--type=service", "--all", "--no-pager",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.warning(f"systemctl list failed (degraded mode): {stderr.decode()}")
                return []
            
            services = []
            lines = stdout.decode().split("\n")
            
            for line in lines[1:]:
                if ".service" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        name = parts[0].replace(".service", "")
                        load_state = parts[1]
                        active_state = parts[2]
                        
                        status = ServiceStatus.UNKNOWN
                        if active_state == "active":
                            status = ServiceStatus.ACTIVE
                        elif active_state == "inactive":
                            status = ServiceStatus.INACTIVE
                        elif active_state == "failed":
                            status = ServiceStatus.FAILED
                        
                        services.append(ServiceInfo(
                            name=name,
                            type=ServiceType.SYSTEMD,
                            status=status,
                            description=" ".join(parts[4:]) if len(parts) > 4 else None,
                            metadata={"load_state": load_state}
                        ))
            
            return services
            
        except Exception as e:
            logger.warning(f"Systemd not available (Replit/degraded mode): {e}")
            return []
    
    async def service_action(self, service_name: str, action: str) -> dict:
        """Execute action on systemd service."""
        try:
            cmd = ["systemctl", action, f"{service_name}.service"]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
            }
            
        except Exception as e:
            logger.error(f"Systemd action error: {e}")
            raise Exception(f"Failed to execute action: {str(e)}")
