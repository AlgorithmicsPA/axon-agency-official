from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload
from app.core.utils import write_audit_log
from app.config import settings
from app.security import require_admin
from app.adapters.flows_n8n import N8nAdapter
from loguru import logger


router = APIRouter(prefix="/api", tags=["flows"])


class TriggerFlowRequest(BaseModel):
    workflow_id: str
    payload: Dict[str, Any] = {}


class TriggerFlowResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}


@router.post("/flows/trigger", response_model=TriggerFlowResponse)
async def trigger_flow(
    request: TriggerFlowRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Trigger an n8n workflow."""
    require_admin(current_user)
    
    if not settings.n8n_base_url:
        raise HTTPException(
            status_code=503,
            detail="n8n not configured. Set N8N_BASE_URL and N8N_API_KEY"
        )
    
    try:
        adapter = N8nAdapter(settings.n8n_base_url, settings.n8n_api_key)
        result = await adapter.trigger_workflow(request.workflow_id, request.payload)
        
        write_audit_log(
            "flow_trigger",
            current_user.sub,
            {"workflow_id": request.workflow_id},
            settings.audit_log_path,
        )
        
        return TriggerFlowResponse(
            success=True,
            message="Workflow triggered",
            data=result,
        )
        
    except Exception as e:
        logger.error(f"Flow trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flows/status")
async def get_flows_status(
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get n8n connection status."""
    if not settings.n8n_base_url:
        return {"available": False, "message": "n8n not configured"}
    
    try:
        adapter = N8nAdapter(settings.n8n_base_url, settings.n8n_api_key)
        is_available = await adapter.check_connection()
        
        return {
            "available": is_available,
            "base_url": settings.n8n_base_url,
            "message": "Connected" if is_available else "Connection failed"
        }
        
    except Exception as e:
        logger.error(f"n8n status check error: {e}")
        return {"available": False, "message": str(e)}
