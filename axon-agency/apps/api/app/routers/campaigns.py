"""Campaign management endpoints."""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Campaign, CampaignStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    """Create campaign request."""
    name: str
    goal: str
    config: dict = {}


@router.post("/create")
async def create_campaign(
    request: CreateCampaignRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new campaign."""
    campaign = Campaign(
        name=request.name,
        goal=request.goal,
        config=request.config,
        status=CampaignStatus.DRAFT.value,
        created_by=1
    )
    
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status}


@router.get("/list")
async def list_campaigns(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all campaigns."""
    campaigns = session.exec(select(Campaign).order_by(Campaign.created_at.desc())).all()
    
    return {
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "goal": c.goal,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            }
            for c in campaigns
        ]
    }


@router.get("/{campaign_id}/status")
async def get_campaign_status(
    campaign_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get campaign execution status."""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
        "results": campaign.results
    }
