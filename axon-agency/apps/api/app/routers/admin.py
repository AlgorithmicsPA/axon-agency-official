"""Admin-only endpoints for system management."""

import logging
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import get_session
from app.core.security import get_current_user, TokenData
from app.routers.tenants import require_admin
from app.routers.orders import generate_order_number
from app.routers.catalog import MOCK_AGENTS
from app.models.tenants import Tenant
from app.models.orders import Order
from app.services.agent_blueprint_service import generate_blueprint

router = APIRouter()
logger = logging.getLogger(__name__)

DEMO_TENANTS = [
    {
        "slug": "algorithmics-academy",
        "name": "Algorithmics AI Academy",
        "business_type": "school",
        "contact_email": "academy@algorithmics.ai",
        "contact_phone": "+52-55-1234-5678",
        "contact_name": "Director Académico",
        "branding": {
            "primary_color": "#4F46E5",
            "secondary_color": "#818CF8",
            "logo_url": None
        },
        "settings": {
            "industry": "Education Technology",
            "max_orders": 50
        },
        "notes": "Academia de programación e IA para niños y jóvenes. Demo tenant."
    },
    {
        "slug": "notaria-17",
        "name": "Notaría 17",
        "business_type": "notary",
        "contact_email": "contacto@notaria17.mx",
        "contact_phone": "+52-55-8765-4321",
        "contact_name": "Titular",
        "branding": {
            "primary_color": "#059669",
            "secondary_color": "#10B981",
            "logo_url": None
        },
        "settings": {
            "industry": "Legal Services",
            "max_orders": 30
        },
        "notes": "Notaría pública especializada en trámites digitales. Demo tenant."
    },
    {
        "slug": "beesmart-delivery",
        "name": "BeeSmart Delivery",
        "business_type": "delivery",
        "contact_email": "soporte@beesmart.delivery",
        "contact_phone": "+52-55-9999-0000",
        "contact_name": "Gerente de Operaciones",
        "branding": {
            "primary_color": "#F59E0B",
            "secondary_color": "#FBBF24",
            "logo_url": None
        },
        "settings": {
            "industry": "Logistics & E-commerce",
            "max_orders": 100
        },
        "notes": "Servicio de mensajería urbana rápida. Demo tenant."
    }
]

DEMO_ORDERS = {
    "algorithmics-academy": [
        {
            "agent_id": "content-generator",
            "nombre_producto": "Generador de Artículos SEO",
            "estado": "listo",
            "prioridad": "alta",
            "description": "Blog educativo con contenido optimizado para keywords como 'cursos programación niños', 'IA educativa'"
        },
        {
            "agent_id": "marketing-autopilot",
            "nombre_producto": "Autopilot Redes Sociales",
            "estado": "construccion",
            "prioridad": "alta",
            "description": "Automatizar posts en Instagram/Facebook con contenido de clases y testimonios"
        },
        {
            "agent_id": "landing-builder",
            "nombre_producto": "Landing Page Inscripciones",
            "estado": "nuevo",
            "prioridad": "media",
            "description": "Landing page para campaña de verano 2025 con formulario de registro"
        }
    ],
    "notaria-17": [
        {
            "agent_id": "whatsapp-autopilot",
            "nombre_producto": "WhatsApp Consultas Legales",
            "estado": "listo",
            "prioridad": "alta",
            "description": "Automatizar respuestas a consultas frecuentes (costos, requisitos, horarios)"
        },
        {
            "agent_id": "landing-builder",
            "nombre_producto": "Landing Testamentos Digitales",
            "estado": "construccion",
            "prioridad": "alta",
            "description": "Landing page especializada en testamentos online con CTA conversión"
        },
        {
            "agent_id": "web-cloner",
            "nombre_producto": "Renovación Portal Notarial",
            "estado": "planificacion",
            "prioridad": "media",
            "description": "Clonar y mejorar sitio actual con mejor UX y trámites digitales"
        }
    ],
    "beesmart-delivery": [
        {
            "agent_id": "whatsapp-autopilot",
            "nombre_producto": "WhatsApp Soporte Clientes",
            "estado": "listo",
            "prioridad": "alta",
            "description": "Bot para rastreo de paquetes, consultas de tarifas, soporte 24/7"
        },
        {
            "agent_id": "qa-automator",
            "nombre_producto": "QA App Móvil Delivery",
            "estado": "construccion",
            "prioridad": "alta",
            "description": "Testing automatizado de flujos críticos (pedido, pago, tracking)"
        },
        {
            "agent_id": "marketing-autopilot",
            "nombre_producto": "Marketing Digital Promociones",
            "estado": "nuevo",
            "prioridad": "media",
            "description": "Campañas automatizadas para promociones flash y descuentos por zona"
        }
    ]
}


@router.post("/seed-demo")
async def seed_demo_data(
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Crear datos de demostración: 3 tenants y 9 órdenes.
    
    Admin-only endpoint. Idempotent - puede ejecutarse múltiples veces sin crear duplicados.
    
    Creates:
    - 3 demo tenants (algorithmics-academy, notaria-17, beesmart-delivery)
    - 9 demo orders (3 per tenant) with realistic data
    
    Returns:
    - Summary with tenants_created and orders_created counts
    """
    require_admin(current_user, session)
    
    tenants_created = 0
    orders_created = 0
    tenant_summary = []
    
    for tenant_data in DEMO_TENANTS:
        slug = tenant_data["slug"]
        
        existing_tenant = session.exec(
            select(Tenant).where(Tenant.slug == slug)
        ).first()
        
        if existing_tenant:
            logger.info(f"Tenant {slug} already exists, skipping creation")
            tenant_id = existing_tenant.id
        else:
            tenant = Tenant(
                slug=tenant_data["slug"],
                name=tenant_data["name"],
                business_type=tenant_data["business_type"],
                contact_email=tenant_data["contact_email"],
                contact_phone=tenant_data["contact_phone"],
                contact_name=tenant_data["contact_name"],
                branding=tenant_data["branding"],
                settings=tenant_data["settings"],
                notes=tenant_data["notes"]
            )
            
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
            
            tenant_id = tenant.id
            tenants_created += 1
            logger.info(f"Created demo tenant: {slug}")
        
        orders_for_tenant = 0
        
        for order_data in DEMO_ORDERS[slug]:
            agent_id = order_data["agent_id"]
            nombre_producto = order_data["nombre_producto"]
            demo_tag = f"demo_{slug}_{agent_id}_{nombre_producto.lower().replace(' ', '_')}"
            
            existing_order = session.exec(
                select(Order).where(
                    Order.tenant_id == tenant_id
                )
            ).all()
            
            demo_order_exists = any(
                o.datos_cliente and o.datos_cliente.get("demo_tag") == demo_tag
                for o in existing_order
            )
            
            if demo_order_exists:
                logger.info(f"Demo order with tag '{demo_tag}' already exists, skipping")
                continue
            
            agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
            if not agent:
                logger.warning(f"Agent {agent_id} not found in catalog, skipping order")
                continue
            
            order_number = generate_order_number(session)
            
            order = Order(
                order_number=order_number,
                tipo_producto=agent_id,
                nombre_producto=nombre_producto,
                estado=order_data["estado"],
                prioridad=order_data["prioridad"],
                tenant_id=tenant_id,
                datos_cliente={
                    "source": "demo_seed",
                    "demo_tag": demo_tag,
                    "tenant_slug": slug,
                    "agent_name": agent["name"],
                    "description": order_data["description"],
                    "submitted_at": datetime.utcnow().isoformat()
                }
            )
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            try:
                blueprint_dict = generate_blueprint(order, agent_id_from_catalog=agent_id)
                order.agent_blueprint = blueprint_dict
                session.add(order)
                session.commit()
                logger.info(f"Generated blueprint for order {order.order_number}")
            except Exception as e:
                logger.warning(f"Failed to generate blueprint for {order.order_number}: {e}")
            
            orders_for_tenant += 1
            orders_created += 1
            logger.info(f"Created demo order: {order_number} for tenant {slug}")
        
        tenant_summary.append({
            "slug": slug,
            "orders": orders_for_tenant
        })
    
    return {
        "success": True,
        "message": "Demo data created successfully",
        "tenants_created": tenants_created,
        "orders_created": orders_created,
        "tenants": tenant_summary
    }
