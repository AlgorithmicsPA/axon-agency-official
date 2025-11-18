import httpx
from typing import Dict, Any
from loguru import logger


class N8nAdapter:
    """Adapter for n8n workflow automation."""
    
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
    
    async def trigger_workflow(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n workflow."""
        url = f"{self.base_url}/webhook/{workflow_id}"
        
        headers = {}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                return response.json() if response.text else {"status": "triggered"}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"n8n HTTP error: {e}")
            raise Exception(f"n8n returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"n8n trigger error: {e}")
            raise Exception(f"Failed to trigger workflow: {str(e)}")
    
    async def check_connection(self) -> bool:
        """Check if n8n is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/healthz")
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"n8n connection check failed: {e}")
            return False
