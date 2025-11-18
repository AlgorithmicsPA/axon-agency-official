import asyncio
from typing import Dict, Any
from loguru import logger


class TailscaleAdapter:
    """Adapter for Tailscale VPN management."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    async def get_status(self) -> Dict[str, Any]:
        """Get tailscale service status."""
        try:
            result = await asyncio.create_subprocess_exec(
                "systemctl", "is-active", self.service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            is_active = stdout.decode().strip() == "active"
            
            status_result = await asyncio.create_subprocess_exec(
                "tailscale", "status", "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            status_stdout, _ = await status_result.communicate()
            
            return {
                "active": is_active,
                "service": self.service_name,
                "status": stdout.decode().strip(),
                "details": status_stdout.decode() if status_result.returncode == 0 else None,
            }
            
        except Exception as e:
            logger.warning(f"Tailscale status check failed: {e}")
            return {
                "active": False,
                "service": self.service_name,
                "error": str(e),
            }
    
    async def restart(self) -> Dict[str, Any]:
        """Restart tailscale service."""
        try:
            result = await asyncio.create_subprocess_exec(
                "systemctl", "restart", self.service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "service": self.service_name,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
            }
            
        except Exception as e:
            logger.error(f"Tailscale restart failed: {e}")
            raise Exception(f"Failed to restart tailscale: {str(e)}")
