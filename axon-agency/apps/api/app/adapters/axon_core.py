"""Axon Core API adapter for remote communication."""

import httpx
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class AxonCoreClient:
    """Client to communicate with Axon Core backend."""
    
    def __init__(self):
        self.base_url = settings.axon_core_api_base.rstrip("/")
        self.token = settings.axon_core_api_token
        self.enabled = settings.axon_core_enabled
        self.timeout = 30.0
        
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to Axon Core API."""
        if not self.enabled:
            logger.warning("Axon Core integration is disabled")
            return None
            
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Axon Core request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error communicating with Axon Core: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if Axon Core is reachable."""
        result = await self._request("GET", "/api/health")
        return result is not None and result.get("status") == "healthy"
    
    async def get_catalog(self) -> Optional[Dict[str, Any]]:
        """Get Axon Core system catalog."""
        return await self._request("GET", "/api/catalog")
    
    async def chat(
        self, 
        text: str, 
        session_id: str,
        model: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send chat message to Axon Core LLM."""
        payload = {
            "text": text,
            "session_id": session_id,
        }
        if model:
            payload["model"] = model
            
        return await self._request("POST", "/api/agent/chat", json=payload)
    
    async def execute_command(
        self, 
        command: str,
        args: Optional[list] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute command on Axon Core."""
        payload = {
            "command": command,
            "args": args or [],
        }
        return await self._request("POST", "/api/commands/run", json=payload)
    
    async def list_services(self) -> Optional[list]:
        """List services from Axon Core."""
        result = await self._request("POST", "/api/services/list")
        if result:
            return result.get("services", [])
        return None
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get system metrics from Axon Core."""
        return await self._request("GET", "/api/metrics")
    
    async def trigger_workflow(
        self,
        workflow_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Trigger n8n workflow on Axon Core."""
        return await self._request(
            "POST", 
            f"/api/flows/trigger/{workflow_id}",
            json=payload or {},
        )


axon_core_client = AxonCoreClient()
