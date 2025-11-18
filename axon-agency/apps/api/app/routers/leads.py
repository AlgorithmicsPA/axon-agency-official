"""Leads router for WhatsApp Sales Agent dashboard."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.security import require_admin
from app.core.config import settings
from app.integrations.mongodb_client import MongoDBClient

router = APIRouter()


class LeadResponse(BaseModel):
    """Lead response model."""
    phone: str
    nombre: Optional[str] = None
    email: Optional[str] = None
    empresa: Optional[str] = None
    sector: Optional[str] = None
    tamano_empresa: Optional[str] = None
    presupuesto_aprox: Optional[str] = None
    linkedin_role: Optional[str] = None
    linkedin_company_size: Optional[str] = None
    linkedin_location: Optional[str] = None
    linkedin_industry: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LeadsListResponse(BaseModel):
    """Leads list response with pagination info."""
    leads: List[LeadResponse]
    total: int


@router.get("/list", response_model=LeadsListResponse)
async def list_leads(
    current_user = Depends(require_admin),
    limit: int = 100,
    skip: int = 0
):
    """
    List all leads from WhatsApp Sales Agent.
    Admin-only endpoint.
    
    Args:
        current_user: Current admin user (from dependency)
        limit: Maximum number of leads to return (default 100)
        skip: Number of leads to skip for pagination (default 0)
        
    Returns:
        LeadsListResponse with leads list and total count
        
    Raises:
        HTTPException 503: MongoDB not configured
        HTTPException 500: Error fetching leads
    """
    if not settings.mongodb_uri:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not configured. WhatsApp Sales Agent leads unavailable."
        )
    
    try:
        mongo = MongoDBClient(uri=settings.mongodb_uri, db_name=settings.mongodb_db_name)
        await mongo.connect()
        
        leads_collection = mongo.db["leads"]
        cursor = leads_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        leads_docs = await cursor.to_list(length=limit)
        
        total = await leads_collection.count_documents({})
        
        await mongo.disconnect()
        
        leads = []
        for doc in leads_docs:
            lead = LeadResponse(
                phone=doc.get("phone", ""),
                nombre=doc.get("nombre"),
                email=doc.get("email"),
                empresa=doc.get("empresa"),
                sector=doc.get("sector"),
                tamano_empresa=doc.get("tamano_empresa"),
                presupuesto_aprox=doc.get("presupuesto_aprox"),
                linkedin_role=doc.get("linkedin_role"),
                linkedin_company_size=doc.get("linkedin_company_size"),
                linkedin_location=doc.get("linkedin_location"),
                linkedin_industry=doc.get("linkedin_industry"),
                created_at=doc.get("created_at"),
                updated_at=doc.get("updated_at")
            )
            leads.append(lead)
        
        return LeadsListResponse(leads=leads, total=total)
    except Exception as e:
        error_msg = str(e)[:200]
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching leads: {error_msg}"
        )
