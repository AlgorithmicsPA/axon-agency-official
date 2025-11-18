"""Axon Core integration router - proxy endpoints to remote Axon Core."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.security import get_current_user
from app.adapters.axon_core import axon_core_client

router = APIRouter(prefix="/api/axon-core", tags=["Axon Core"])


class ChatRequest(BaseModel):
    text: str
    session_id: str
    model: Optional[str] = None


class CommandRequest(BaseModel):
    command: str
    args: Optional[list] = None


class WorkflowRequest(BaseModel):
    workflow_id: str
    payload: Optional[Dict[str, Any]] = None


@router.get("/health")
async def axon_core_health():
    """Check Axon Core connectivity."""
    is_healthy = await axon_core_client.health_check()
    
    if not is_healthy:
        raise HTTPException(
            status_code=503, 
            detail="Axon Core is not reachable"
        )
    
    return {
        "status": "connected",
        "remote": axon_core_client.base_url,
    }


@router.get("/catalog")
async def axon_core_catalog():
    """Get Axon Core system catalog."""
    catalog = await axon_core_client.get_catalog()
    
    if not catalog:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch catalog from Axon Core"
        )
    
    return catalog


@router.post("/chat")
async def axon_core_chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """Chat with Axon Core LLM."""
    response = await axon_core_client.chat(
        text=request.text,
        session_id=request.session_id,
        model=request.model,
    )
    
    if not response:
        raise HTTPException(
            status_code=503,
            detail="Axon Core chat service unavailable"
        )
    
    return response


@router.post("/command")
async def axon_core_command(
    request: CommandRequest,
    user: dict = Depends(get_current_user),
):
    """Execute command on Axon Core."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    response = await axon_core_client.execute_command(
        command=request.command,
        args=request.args,
    )
    
    if not response:
        raise HTTPException(
            status_code=503,
            detail="Axon Core command service unavailable"
        )
    
    return response


@router.get("/services")
async def axon_core_services(user: dict = Depends(get_current_user)):
    """List services from Axon Core."""
    services = await axon_core_client.list_services()
    
    if services is None:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch services from Axon Core"
        )
    
    return {"services": services}


@router.get("/metrics")
async def axon_core_metrics(user: dict = Depends(get_current_user)):
    """Get system metrics from Axon Core."""
    metrics = await axon_core_client.get_metrics()
    
    if not metrics:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch metrics from Axon Core"
        )
    
    return metrics


@router.post("/workflow")
async def axon_core_workflow(
    request: WorkflowRequest,
    user: dict = Depends(get_current_user),
):
    """Trigger n8n workflow on Axon Core."""
    response = await axon_core_client.trigger_workflow(
        workflow_id=request.workflow_id,
        payload=request.payload,
    )
    
    if not response:
        raise HTTPException(
            status_code=503,
            detail="Axon Core workflow service unavailable"
        )
    
    return response
