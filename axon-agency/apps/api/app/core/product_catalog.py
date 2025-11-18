"""
Product catalog and template mapping.
Defines available autopilot products and their associated templates/channels.
"""

from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class ProductType(str, Enum):
    """Product types available in the system."""
    WHATSAPP_CORE = "whatsapp_core"
    WHATSAPP_SALES = "whatsapp_sales"
    SOCIAL_AUTOPILOT = "social_autopilot"
    TELEGRAM_BROADCAST = "telegram_broadcast"
    EMAIL_AUTOPILOT = "email_autopilot"
    SLACK_BOT = "slack_bot"


class ChannelType(str, Enum):
    """Channel types for autopilot products."""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SOCIAL = "social"
    EMAIL = "email"
    SLACK = "slack"


class ProductDefinition(BaseModel):
    """Product/Autopilot definition."""
    product_type: ProductType
    name: str
    description: str
    channels: List[ChannelType]
    template_module: Optional[str] = None
    template_function: Optional[str] = None
    deploy_endpoint: Optional[str] = None
    required_env_vars: List[str]
    optional_env_vars: List[str] = []
    available: bool = True


PRODUCT_CATALOG: dict[ProductType, ProductDefinition] = {
    ProductType.WHATSAPP_CORE: ProductDefinition(
        product_type=ProductType.WHATSAPP_CORE,
        name="WhatsApp Autopilot Core",
        description="Autopilot básico de WhatsApp con respuestas automáticas vía n8n webhook",
        channels=[ChannelType.WHATSAPP],
        template_module=None,
        template_function=None,
        deploy_endpoint="/api/orders/{order_id}/deploy/whatsapp",
        required_env_vars=["N8N_WHATSAPP_DEPLOY_WEBHOOK_URL"],
        optional_env_vars=[],
        available=True
    ),
    ProductType.WHATSAPP_SALES: ProductDefinition(
        product_type=ProductType.WHATSAPP_SALES,
        name="WhatsApp Sales Agent (Full IntegraIA)",
        description="Agente conversacional de sales qualification con 7 integraciones: MongoDB, OpenAI, Melvis RAG, Tavily web search, LinkedIn enrichment, Stripe checkout, Cal.com booking",
        channels=[ChannelType.WHATSAPP],
        template_module="app.templates.whatsapp_template_full_integraia",
        template_function="handle_whatsapp_webhook",
        deploy_endpoint="/api/orders/{order_id}/deploy/whatsapp",
        required_env_vars=["MONGODB_URI", "OPENAI_API_KEY"],
        optional_env_vars=["MELVIS_API_KEY", "TAVILY_API_KEY", "LINKEDIN_API_KEY", "STRIPE_SECRET_KEY", "CALCOM_BOOKING_LINK"],
        available=True
    ),
    ProductType.SOCIAL_AUTOPILOT: ProductDefinition(
        product_type=ProductType.SOCIAL_AUTOPILOT,
        name="Social Media Autopilot (Ayrshare)",
        description="Publicación automática a Twitter, Facebook e Instagram vía Ayrshare API",
        channels=[ChannelType.SOCIAL],
        template_module=None,
        template_function=None,
        deploy_endpoint="/api/orders/{order_id}/deploy/social",
        required_env_vars=["AYRSHARE_API_KEY", "ENABLE_AYRSHARE_SOCIAL"],
        optional_env_vars=[],
        available=True
    ),
    ProductType.TELEGRAM_BROADCAST: ProductDefinition(
        product_type=ProductType.TELEGRAM_BROADCAST,
        name="Telegram Broadcast Bot",
        description="Bot de Telegram para broadcasts y mensajes automáticos con soporte de media (fotos, grupos)",
        channels=[ChannelType.TELEGRAM],
        template_module=None,
        template_function=None,
        deploy_endpoint="/api/orders/{order_id}/deploy/telegram",
        required_env_vars=["TELEGRAM_BOT_TOKEN", "ENABLE_TELEGRAM_DEPLOY"],
        optional_env_vars=["DEFAULT_TELEGRAM_CHAT_ID"],
        available=True
    ),
    ProductType.EMAIL_AUTOPILOT: ProductDefinition(
        product_type=ProductType.EMAIL_AUTOPILOT,
        name="Email Autopilot",
        description="Campañas de email automáticas con seguimiento",
        channels=[ChannelType.EMAIL],
        template_module=None,
        template_function=None,
        deploy_endpoint=None,
        required_env_vars=[],
        optional_env_vars=[],
        available=False
    ),
    ProductType.SLACK_BOT: ProductDefinition(
        product_type=ProductType.SLACK_BOT,
        name="Slack Bot",
        description="Bot de Slack para automatizaciones internas",
        channels=[ChannelType.SLACK],
        template_module=None,
        template_function=None,
        deploy_endpoint=None,
        required_env_vars=[],
        optional_env_vars=[],
        available=False
    ),
}


def get_product_definition(product_type: str) -> Optional[ProductDefinition]:
    """Get product definition by product_type string."""
    try:
        pt = ProductType(product_type)
        return PRODUCT_CATALOG.get(pt)
    except ValueError:
        return None


def get_available_products() -> List[ProductDefinition]:
    """Get all available products (available=True)."""
    return [p for p in PRODUCT_CATALOG.values() if p.available]
