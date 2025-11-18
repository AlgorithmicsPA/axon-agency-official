"""External integrations (WhatsApp, Telegram, Social) endpoints."""

import logging
import asyncio
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from app.core.security import get_current_user
from app.core.config import settings
from app.core.database import get_session
from app.models.orders import Order
from app.integrations.ayrshare_client import get_rate_limit_info
from app.integrations.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

router = APIRouter()


class RateLimitInfo(BaseModel):
    """Rate limit information for API usage."""
    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_at: Optional[datetime] = None


class SocialHealthResponse(BaseModel):
    """Health check response for social media integration."""
    status: Literal["disabled", "misconfigured", "healthy"]
    provider: str = "ayrshare"
    enabled_platforms: List[str]
    rate_limit: RateLimitInfo
    last_deploy_success: Optional[datetime] = None
    error_message: Optional[str] = None


class IntegrationHealth(BaseModel):
    """Health status for a single integration."""
    name: str
    status: Literal["healthy", "degraded", "disabled"]
    message: Optional[str] = None
    last_activity: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None


class UnifiedHealthResponse(BaseModel):
    """Unified health check response for all integrations."""
    overall_status: Literal["healthy", "degraded", "disabled"]
    timestamp: datetime
    integrations: List[IntegrationHealth]


@router.get("/whatsapp/webhook")
async def whatsapp_verify(request: Request):
    """WhatsApp webhook verification."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == "axon-verify-token" and challenge:
        logger.info("WhatsApp webhook verified")
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    body = await request.json()
    logger.info(f"WhatsApp webhook received: {body}")
    
    return {"status": "ok"}


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates."""
    body = await request.json()
    logger.info(f"Telegram webhook received: {body}")
    
    return {"ok": True}


@router.get("/whatsapp/status")
async def whatsapp_status(current_user = Depends(get_current_user)):
    """Get WhatsApp integration status."""
    return {
        "enabled": True,
        "webhook_url": "/api/integrations/whatsapp/webhook",
        "verify_token": "axon-verify-token"
    }


@router.get("/telegram/status")
async def telegram_status(current_user = Depends(get_current_user)):
    """Get Telegram integration status."""
    return {
        "enabled": True,
        "webhook_url": "/api/integrations/telegram/webhook"
    }


@router.get("/social/health", response_model=SocialHealthResponse)
async def social_health_check(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get Ayrshare social media integration health status.
    
    FASE 10.A - Social Health Check Endpoint
    
    Returns the current status of Ayrshare integration including:
    - Configuration status (disabled, misconfigured, healthy)
    - Enabled platforms
    - Rate limit info (from Ayrshare API)
    - Last successful deploy timestamp (from Order.deploy_history)
    - Error messages if any
    
    Status logic:
    - "disabled": ENABLE_AYRSHARE_SOCIAL=false
    - "misconfigured": ENABLE_AYRSHARE_SOCIAL=true but AYRSHARE_API_KEY is empty
    - "healthy": ENABLE_AYRSHARE_SOCIAL=true AND AYRSHARE_API_KEY is configured
    """
    # Determine integration status based on settings
    status: Literal["disabled", "misconfigured", "healthy"]
    error_message: Optional[str] = None
    
    if not settings.enable_ayrshare_social:
        status = "disabled"
        error_message = "Social deploy feature is disabled. Set ENABLE_AYRSHARE_SOCIAL=true to enable."
    elif not settings.ayrshare_api_key or not settings.ayrshare_api_key.strip():
        status = "misconfigured"
        error_message = "Ayrshare API key not configured. Set AYRSHARE_API_KEY environment variable."
    else:
        status = "healthy"
        error_message = None
    
    rate_limit_data = get_rate_limit_info()
    if rate_limit_data:
        rate_limit = RateLimitInfo(
            remaining=rate_limit_data.get("remaining"),
            limit=rate_limit_data.get("limit"),
            reset_at=None
        )
    else:
        rate_limit = RateLimitInfo(remaining=None, limit=None, reset_at=None)
    
    # Query last successful social deploy from Order.deploy_history
    last_deploy_success: Optional[datetime] = None
    
    try:
        statement = select(Order).where(Order.deploy_history != None)
        orders = session.exec(statement).all()
        
        latest_timestamp = None
        for order in orders:
            if order.deploy_history:
                for event in order.deploy_history:
                    if (event.get("channel") == "social" and 
                        event.get("status") == "success" and 
                        event.get("completed_at")):
                        
                        event_timestamp = event.get("completed_at")
                        try:
                            if isinstance(event_timestamp, str):
                                event_dt = datetime.fromisoformat(event_timestamp.replace("Z", "+00:00"))
                            elif isinstance(event_timestamp, datetime):
                                event_dt = event_timestamp
                            else:
                                continue
                            
                            if latest_timestamp is None or event_dt > latest_timestamp:
                                latest_timestamp = event_dt
                        except (ValueError, AttributeError, TypeError):
                            continue
        
        last_deploy_success = latest_timestamp
    except Exception as e:
        logger.warning(f"Error querying deploy_history: {e}")
        last_deploy_success = None
    
    # TODO: Make platforms configurable per-tenant
    # For now, hardcoded default platforms
    enabled_platforms = ["twitter", "facebook", "instagram"]
    
    return SocialHealthResponse(
        status=status,
        provider="ayrshare",
        enabled_platforms=enabled_platforms,
        rate_limit=rate_limit,
        last_deploy_success=last_deploy_success,
        error_message=error_message
    )


async def check_mongodb_health() -> IntegrationHealth:
    """Check MongoDB connection health for WhatsApp Sales Agent.
    
    Returns:
        IntegrationHealth with status:
        - disabled: MONGODB_URI not configured
        - degraded: Connection failed
        - healthy: Connection successful
    """
    if not settings.mongodb_uri or not settings.mongodb_uri.strip():
        return IntegrationHealth(
            name="mongodb",
            status="disabled",
            message="MongoDB not configured (MONGODB_URI missing)"
        )
    
    try:
        client = MongoDBClient(settings.mongodb_uri, settings.mongodb_db_name)
        await client.connect()
        await client.disconnect()
        
        return IntegrationHealth(
            name="mongodb",
            status="healthy",
            message="MongoDB connected successfully",
            details={"database": settings.mongodb_db_name}
        )
    except Exception as e:
        error_msg = str(e)[:100]
        logger.warning(f"MongoDB health check failed: {error_msg}")
        return IntegrationHealth(
            name="mongodb",
            status="degraded",
            message=f"MongoDB connection failed: {error_msg}"
        )


async def check_whatsapp_core_health() -> IntegrationHealth:
    """Check WhatsApp Core (n8n webhook) configuration.
    
    Returns:
        IntegrationHealth with status:
        - disabled: N8N_WHATSAPP_DEPLOY_WEBHOOK_URL not configured
        - healthy: Webhook URL configured
    """
    if not settings.n8n_whatsapp_deploy_webhook_url or not settings.n8n_whatsapp_deploy_webhook_url.strip():
        return IntegrationHealth(
            name="whatsapp_core",
            status="disabled",
            message="WhatsApp Core webhook not configured (N8N_WHATSAPP_DEPLOY_WEBHOOK_URL missing)"
        )
    
    return IntegrationHealth(
        name="whatsapp_core",
        status="healthy",
        message="WhatsApp Core webhook configured",
        details={"webhook_url": settings.n8n_whatsapp_deploy_webhook_url[:50] + "..."}
    )


async def check_whatsapp_sales_agent_health() -> IntegrationHealth:
    """Check WhatsApp Sales Agent (Full IntegraIA) dependencies.
    
    Returns:
        IntegrationHealth with status:
        - disabled: Missing required dependencies (MongoDB or OpenAI)
        - healthy: Core dependencies configured
        
    Details include status of optional integrations (Melvis, Tavily, LinkedIn, Stripe, Cal.com)
    """
    missing_deps = []
    
    if not settings.mongodb_uri or not settings.mongodb_uri.strip():
        missing_deps.append("MongoDB")
    
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        missing_deps.append("OpenAI API key")
    
    if missing_deps:
        return IntegrationHealth(
            name="whatsapp_sales_agent",
            status="disabled",
            message=f"Missing required dependencies: {', '.join(missing_deps)}"
        )
    
    optional_integrations = {
        "melvis": bool(settings.melvis_api_key and settings.melvis_api_key.strip()),
        "tavily": bool(settings.tavily_api_key and settings.tavily_api_key.strip()),
        "linkedin": bool(settings.linkedin_api_key and settings.linkedin_api_key.strip()),
        "stripe": bool(settings.stripe_secret_key and settings.stripe_secret_key.strip()),
        "calcom": bool(settings.calcom_booking_link and settings.calcom_booking_link.strip())
    }
    
    enabled_count = sum(1 for v in optional_integrations.values() if v)
    
    return IntegrationHealth(
        name="whatsapp_sales_agent",
        status="healthy",
        message=f"Core dependencies configured. {enabled_count}/5 optional integrations enabled.",
        details={"optional_integrations": optional_integrations}
    )


async def check_social_health_simple(session: Session) -> IntegrationHealth:
    """Check Ayrshare social media integration health (simplified for unified endpoint).
    
    Reuses logic from /social/health endpoint but returns IntegrationHealth format.
    
    Returns:
        IntegrationHealth with status:
        - disabled: ENABLE_AYRSHARE_SOCIAL=false
        - degraded: Enabled but API key missing
        - healthy: Fully configured
    """
    if not settings.enable_ayrshare_social:
        return IntegrationHealth(
            name="social",
            status="disabled",
            message="Social deploy feature disabled (ENABLE_AYRSHARE_SOCIAL=false)"
        )
    
    if not settings.ayrshare_api_key or not settings.ayrshare_api_key.strip():
        return IntegrationHealth(
            name="social",
            status="degraded",
            message="Ayrshare API key not configured (AYRSHARE_API_KEY missing)"
        )
    
    rate_limit_data = get_rate_limit_info()
    rate_limit_info = None
    if rate_limit_data:
        rate_limit_info = {
            "remaining": rate_limit_data.get("remaining"),
            "limit": rate_limit_data.get("limit")
        }
    
    last_deploy_success: Optional[datetime] = None
    try:
        statement = select(Order).where(Order.deploy_history != None)
        orders = session.exec(statement).all()
        
        latest_timestamp = None
        for order in orders:
            if order.deploy_history:
                for event in order.deploy_history:
                    if (event.get("channel") == "social" and 
                        event.get("status") == "success" and 
                        event.get("completed_at")):
                        
                        event_timestamp = event.get("completed_at")
                        try:
                            if isinstance(event_timestamp, str):
                                event_dt = datetime.fromisoformat(event_timestamp.replace("Z", "+00:00"))
                            elif isinstance(event_timestamp, datetime):
                                event_dt = event_timestamp
                            else:
                                continue
                            
                            if latest_timestamp is None or event_dt > latest_timestamp:
                                latest_timestamp = event_dt
                        except (ValueError, AttributeError, TypeError):
                            continue
        
        last_deploy_success = latest_timestamp
    except Exception as e:
        logger.warning(f"Error querying social deploy_history: {e}")
    
    return IntegrationHealth(
        name="social",
        status="healthy",
        message="Ayrshare integration configured",
        last_activity=last_deploy_success,
        details={
            "provider": "ayrshare",
            "platforms": ["twitter", "facebook", "instagram"],
            "rate_limit": rate_limit_info
        }
    )


async def check_telegram_health() -> IntegrationHealth:
    """Check Telegram bot integration configuration.
    
    Returns:
        IntegrationHealth with status:
        - disabled: Feature flag disabled or bot token missing
        - healthy: Both feature flag and bot token configured
    """
    if not settings.enable_telegram_deploy:
        return IntegrationHealth(
            name="telegram",
            status="disabled",
            message="Telegram deploy disabled (ENABLE_TELEGRAM_DEPLOY=false)"
        )
    
    if not settings.telegram_bot_token or not settings.telegram_bot_token.strip():
        return IntegrationHealth(
            name="telegram",
            status="disabled",
            message="Telegram bot token not configured (TELEGRAM_BOT_TOKEN missing)"
        )
    
    details = {
        "bot_token_configured": True,
        "default_chat_id_configured": bool(settings.default_telegram_chat_id and settings.default_telegram_chat_id.strip())
    }
    
    return IntegrationHealth(
        name="telegram",
        status="healthy",
        message="Telegram bot configured",
        details=details
    )


@router.get("/health", response_model=UnifiedHealthResponse)
async def unified_health_check(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get unified health status for all integrations.
    
    FASE 11 - Unified Health Check Endpoint
    
    Consolidates health status of ALL system integrations:
    1. MongoDB (WhatsApp Sales Agent persistence)
    2. WhatsApp Core (n8n webhook)
    3. WhatsApp Sales Agent (Full IntegraIA)
    4. Social/Ayrshare (social media deploy)
    5. Telegram (bot deploy)
    
    Returns:
        UnifiedHealthResponse with:
        - overall_status: "healthy" (at least 1 healthy), "degraded" (at least 1 degraded), "disabled" (all disabled)
        - timestamp: Current UTC timestamp
        - integrations: List of IntegrationHealth for each integration
        
    Overall status logic:
    - "degraded": At least one integration is degraded
    - "disabled": All integrations are disabled
    - "healthy": At least one integration is healthy and none are degraded
    """
    integrations = await asyncio.gather(
        check_mongodb_health(),
        check_whatsapp_core_health(),
        check_whatsapp_sales_agent_health(),
        check_social_health_simple(session),
        check_telegram_health()
    )
    
    integrations_list = list(integrations)
    
    if any(i.status == "degraded" for i in integrations_list):
        overall_status: Literal["healthy", "degraded", "disabled"] = "degraded"
    elif all(i.status == "disabled" for i in integrations_list):
        overall_status = "disabled"
    else:
        overall_status = "healthy"
    
    return UnifiedHealthResponse(
        overall_status=overall_status,
        timestamp=datetime.utcnow(),
        integrations=integrations_list
    )
