"""
Agent Blueprint Service - FASE 3.A

Servicio para generar AgentBlueprints automáticamente a partir de Orders.
Define QUÉ se va a construir: tipo de agente, fuentes, canales, capacidades.
"""

from typing import Optional
from app.models.orders import Order, AgentBlueprint, SourceConfig


# Mapeos de tipo_producto → agent_type y capabilities por defecto
AGENT_TYPE_MAPPING = {
    "whatsapp_autopilot": {
        "agent_type": "whatsapp_sales",
        "channels": ["whatsapp"],
        "capabilities": ["ventas", "soporte", "consultas", "faq"],
        "automation_level": "semi",
    },
    "autopilot_whatsapp": {
        "agent_type": "whatsapp_sales",
        "channels": ["whatsapp"],
        "capabilities": ["ventas", "soporte", "consultas", "faq"],
        "automation_level": "semi",
    },
    "autopilot_ventas": {
        "agent_type": "sales_agent",
        "channels": ["webchat", "email"],
        "capabilities": ["ventas", "prospección", "seguimiento", "cotizaciones"],
        "automation_level": "semi",
    },
    "webhook_service": {
        "agent_type": "webhook_processor",
        "channels": ["api", "webhook"],
        "capabilities": ["procesamiento", "notificaciones", "integraciones"],
        "automation_level": "full",
    },
    "marketing_autopilot": {
        "agent_type": "marketing_automation",
        "channels": ["email", "social_media", "webchat"],
        "capabilities": ["marketing", "campaigns", "analytics", "content"],
        "automation_level": "semi",
    },
    "web_cloner": {
        "agent_type": "web_support",
        "channels": ["webchat", "email"],
        "capabilities": ["soporte", "faq", "información", "navegación"],
        "automation_level": "semi",
    },
    "landing_builder": {
        "agent_type": "education_agent",
        "channels": ["landing_page", "email"],
        "capabilities": ["información", "registro", "seguimiento"],
        "automation_level": "semi",
    },
    "qa_automator": {
        "agent_type": "qa_agent",
        "channels": ["internal", "api"],
        "capabilities": ["testing", "validation", "reporting"],
        "automation_level": "full",
    },
    "content_generator": {
        "agent_type": "content_creator",
        "channels": ["api", "webchat"],
        "capabilities": ["content_creation", "copywriting", "seo"],
        "automation_level": "semi",
    },
}


def generate_blueprint(
    order: Order,
    agent_id_from_catalog: Optional[str] = None
) -> dict:
    """
    Genera un AgentBlueprint a partir de una Order.
    
    Args:
        order: La orden desde la cual generar el blueprint
        agent_id_from_catalog: ID del agente seleccionado en catálogo (si aplica)
    
    Returns:
        dict: Blueprint serializado listo para guardar en Order.agent_blueprint
    """
    
    # Normalizar tipo_producto: convertir guiones a guiones bajos y lowercase
    # Esto maneja tanto "marketing-autopilot" (catálogo) como "marketing_autopilot" (directo)
    tipo = order.tipo_producto.lower().replace("-", "_")
    config = AGENT_TYPE_MAPPING.get(tipo, {
        "agent_type": "generic_agent",
        "channels": ["webchat"],
        "capabilities": ["soporte", "consultas"],
        "automation_level": "semi",
    })
    
    # Extraer sources de datos_cliente
    sources = _extract_sources_from_client_data(order.datos_cliente)
    
    # Extraer client_profile si hay info relevante
    client_profile = _extract_client_profile(order.datos_cliente)
    
    # Generar notas descriptivas
    notes = _generate_notes(order, agent_id_from_catalog)
    
    # Crear blueprint
    blueprint = AgentBlueprint(
        version="1.0",
        agent_type=config["agent_type"],
        product_type=order.tipo_producto,
        sources=sources,
        channels=config["channels"],
        capabilities=config["capabilities"],
        automation_level=config["automation_level"],
        client_profile=client_profile,
        notes=notes,
    )
    
    # Retornar como dict (para guardarlo en JSON)
    return blueprint.model_dump()


def _extract_sources_from_client_data(datos_cliente: dict) -> list[SourceConfig]:
    """
    Extrae fuentes de información de datos_cliente.
    
    Busca claves como:
    - website_url / url / sitio_web
    - manual_input / descripcion / information
    - faq_file / documento
    """
    sources = []
    
    # Buscar URL del sitio web
    website_url = (
        datos_cliente.get("website_url") or
        datos_cliente.get("url") or
        datos_cliente.get("sitio_web") or
        datos_cliente.get("configuracion", {}).get("website_url")
    )
    
    if website_url:
        sources.append(SourceConfig(
            type="website_url",
            value=website_url,
            notes="Sitio web principal del cliente"
        ))
    
    # Buscar descripción manual
    description = (
        datos_cliente.get("description") or
        datos_cliente.get("descripcion") or
        datos_cliente.get("configuracion", {}).get("description")
    )
    
    if description:
        sources.append(SourceConfig(
            type="manual_input",
            value=description,
            notes="Descripción proporcionada por el cliente"
        ))
    
    # Buscar archivos FAQ u otros documentos
    faq_file = datos_cliente.get("faq_file")
    if faq_file:
        sources.append(SourceConfig(
            type="faq_file",
            value=faq_file,
            notes="Archivo de preguntas frecuentes"
        ))
    
    # Si no hay sources, agregar uno genérico
    if not sources:
        sources.append(SourceConfig(
            type="to_be_defined",
            value="Pendiente de configuración",
            notes="El cliente aún no ha proporcionado fuentes de información específicas"
        ))
    
    return sources


def _extract_client_profile(datos_cliente: dict) -> Optional[dict]:
    """
    Extrae perfil del cliente si hay info relevante.
    """
    profile = {}
    
    # Email de contacto
    contact_email = (
        datos_cliente.get("contact_email") or
        datos_cliente.get("email") or
        datos_cliente.get("configuracion", {}).get("contact_email")
    )
    if contact_email:
        profile["contact_email"] = contact_email
    
    # Nombre del negocio
    business_name = (
        datos_cliente.get("business_name") or
        datos_cliente.get("empresa") or
        datos_cliente.get("configuracion", {}).get("business_name")
    )
    if business_name:
        profile["business_name"] = business_name
    
    # Industria
    industry = datos_cliente.get("industry") or datos_cliente.get("industria")
    if industry:
        profile["industry"] = industry
    
    return profile if profile else None


def _generate_notes(order: Order, agent_id_from_catalog: Optional[str]) -> str:
    """
    Genera notas descriptivas para el blueprint.
    """
    notes_parts = []
    
    if agent_id_from_catalog:
        notes_parts.append(f"Agente seleccionado desde catálogo: {agent_id_from_catalog}")
    
    notes_parts.append(f"Producto: {order.nombre_producto}")
    notes_parts.append(f"Orden: {order.order_number}")
    
    if order.tags:
        notes_parts.append(f"Tags: {', '.join(order.tags)}")
    
    return " | ".join(notes_parts)
