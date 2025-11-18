"""Catalog endpoints - Agent listings and order creation."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_session
from app.models.orders import Order
from app.services.agent_blueprint_service import generate_blueprint

logger = logging.getLogger(__name__)

router = APIRouter()


MOCK_AGENTS = [
    {
        "id": "marketing-autopilot",
        "name": "Marketing Autopilot",
        "description": "Automatiza campañas en redes sociales con IA",
        "category": "Marketing",
        "icon": "megaphone",
        "capabilities": [
            "Generación automática de contenido",
            "Programación de publicaciones",
            "Análisis de engagement",
            "Optimización de campañas"
        ],
        "pricing": "Desde $99/mes"
    },
    {
        "id": "web-cloner",
        "name": "Intelligent Web Cloner",
        "description": "Clona y mejora sitios web automáticamente",
        "category": "Development",
        "icon": "code",
        "capabilities": [
            "Análisis inteligente de sitios",
            "Clonación con mejoras UX/UI",
            "Optimización de performance",
            "SEO automático"
        ],
        "pricing": "Desde $199/proyecto"
    },
    {
        "id": "whatsapp-autopilot",
        "name": "WhatsApp Autopilot",
        "description": "Automatización completa de WhatsApp Business",
        "category": "Communication",
        "icon": "phone",
        "capabilities": [
            "Respuestas automáticas con IA",
            "Gestión de conversaciones",
            "Integración con CRM",
            "Analytics en tiempo real"
        ],
        "pricing": "Desde $149/mes"
    },
    {
        "id": "landing-builder",
        "name": "AI Landing Builder",
        "description": "Crea landing pages de alta conversión con IA",
        "category": "Development",
        "icon": "layout",
        "capabilities": [
            "Diseño automático basado en objetivos",
            "A/B testing inteligente",
            "Optimización de conversión",
            "Integración con analytics"
        ],
        "pricing": "Desde $79/proyecto"
    },
    {
        "id": "qa-automator",
        "name": "QA Automator",
        "description": "Testing y QA automatizado con IA",
        "category": "Quality Assurance",
        "icon": "check-circle",
        "capabilities": [
            "Testing automático E2E",
            "Detección de bugs con IA",
            "Generación de test cases",
            "Reportes detallados"
        ],
        "pricing": "Desde $129/mes"
    },
    {
        "id": "content-generator",
        "name": "Content Generator Pro",
        "description": "Generación masiva de contenido SEO",
        "category": "Marketing",
        "icon": "file-text",
        "capabilities": [
            "Artículos optimizados para SEO",
            "Investigación automática de keywords",
            "Generación multilenguaje",
            "Publicación automatizada"
        ],
        "pricing": "Desde $89/mes"
    }
]


class CatalogOrderRequest(BaseModel):
    """Request to create order from catalog."""
    agent_id: str
    website_url: str
    description: str
    contact_email: Optional[str] = None


class CatalogOrderResponse(BaseModel):
    """Response after creating catalog order."""
    order_id: str
    status: str
    message: str


@router.get("/agents")
async def list_agents():
    """Get list of available agents in catalog."""
    return {
        "agents": MOCK_AGENTS,
        "total": len(MOCK_AGENTS)
    }


@router.get("/agents/{agent_id}")
async def get_agent_detail(agent_id: str):
    """Get detailed information about specific agent."""
    agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    return agent


@router.post("/orders", response_model=CatalogOrderResponse)
async def create_catalog_order(
    request: CatalogOrderRequest,
    session: Session = Depends(get_session)
):
    """Create new order from catalog form submission."""
    
    agent = next((a for a in MOCK_AGENTS if a["id"] == request.agent_id), None)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent_id: {request.agent_id}"
        )
    
    from app.routers.orders import generate_order_number
    
    order_number = generate_order_number(session)
    
    order = Order(
        order_number=order_number,
        tipo_producto=request.agent_id,
        nombre_producto=agent['name'],
        estado="nuevo",
        datos_cliente={
            "source": "catalog",
            "agent_name": agent["name"],
            "website_url": request.website_url,
            "contact_email": request.contact_email,
            "description": request.description,
            "submitted_at": datetime.utcnow().isoformat()
        }
    )
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    try:
        blueprint_dict = generate_blueprint(order, agent_id_from_catalog=request.agent_id)
        order.agent_blueprint = blueprint_dict
        session.add(order)
        session.commit()
        logger.info(f"Generated blueprint for order {order.order_number}")
    except Exception as e:
        logger.warning(f"Failed to generate blueprint for {order.order_number}: {e}")
    
    logger.info(f"Created catalog order {order.order_number} for agent {request.agent_id}")
    
    return CatalogOrderResponse(
        order_id=order.order_number,
        status="nuevo",
        message=f"Orden creada exitosamente. ID: {order.order_number}"
    )
