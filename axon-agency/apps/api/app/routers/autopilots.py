"""Autopilots/agents management endpoints."""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Autopilot

logger = logging.getLogger(__name__)

router = APIRouter()


class TriggerRequest(BaseModel):
    """Trigger autopilot request."""
    name: str
    payload: dict = {}


@router.get("/list")
async def list_autopilots(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List registered autopilots."""
    autopilots = session.exec(
        select(Autopilot).where(Autopilot.is_active == True).order_by(Autopilot.name)
    ).all()
    
    return {
        "items": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "last_run_at": a.last_run_at.isoformat() if a.last_run_at else None
            }
            for a in autopilots
        ]
    }


@router.post("/trigger")
async def trigger_autopilot(
    request: TriggerRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Trigger an autopilot execution."""
    autopilot = session.exec(
        select(Autopilot).where(Autopilot.name == request.name)
    ).first()
    
    if not autopilot:
        raise HTTPException(status_code=404, detail="Autopilot not found")
    
    autopilot.last_run_at = datetime.utcnow()
    session.add(autopilot)
    session.commit()
    
    import uuid
    run_id = str(uuid.uuid4())
    
    logger.info(f"Autopilot '{request.name}' triggered with run_id: {run_id}")
    
    return {"runId": run_id, "status": "triggered"}
