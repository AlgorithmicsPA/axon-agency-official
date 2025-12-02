"""Application configuration using pydantic-settings."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Force load .env file from api directory
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Server
    bind: str = "0.0.0.0"
    port: int = 8080
    
    # Database
    database_url: str = "sqlite:///./axon.db"
    
    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_iss: str = "axon"
    jwt_aud: str = "control"
    jwt_expiration_minutes: int = 1440
    
    # Mode
    production_mode: bool = False
    dev_mode: bool = False  # Must be explicitly enabled for development
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5200,http://127.0.0.1:5200,http://192.168.200.32:5200"
    
    @field_validator("allowed_origins")
    @classmethod
    def parse_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    # OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o"
    
    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"  # Gemini 2.0 Flash - Latest stable model
    gemini_flash_model: str = "gemini-2.0-flash-exp"
    
    # Local Services
    ollama_enabled: bool = False
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.1"
    n8n_base_url: str = "http://127.0.0.1:5679"
    n8n_api_key: str = ""
    n8n_whatsapp_deploy_webhook_url: str = ""
    
    # Ayrshare Social Media Integration (FASE 9.S)
    ayrshare_api_key: str = ""
    ayrshare_base_url: str = "https://app.ayrshare.com/api"
    enable_ayrshare_social: bool = False
    
    # ===========================
    # TELEGRAM DEPLOY (FASE 10.B)
    # ===========================
    # Dual feature flag gating:
    # 1. enable_telegram_deploy: rollout switch (dark rollout support)
    # 2. telegram_bot_token: credentials must be configured
    #
    # Telegram deploy only works when BOTH flags are enabled.
    # This allows storing bot token in prod without activating feature.
    telegram_bot_token: str = Field(
        default="",
        description="Telegram Bot API token. Obtain from @BotFather. If empty, Telegram deploy is disabled."
    )
    
    telegram_base_url: str = Field(
        default="https://api.telegram.org",
        description="Telegram Bot API base URL. Default: https://api.telegram.org"
    )
    
    default_telegram_chat_id: str = Field(
        default="",
        description=(
            "Default Telegram chat_id to use when order does not have telegram_chat_id in deliverable_metadata. "
            "Leave empty to require per-order configuration. "
            "Example: '123456789' or '@channel_username'"
        )
    )
    
    enable_telegram_deploy: bool = Field(
        default=False,
        description="Feature flag to enable Telegram deploy. Must be True AND telegram_bot_token configured to work."
    )
    
    # ========================================
    # WHATSAPP SALES AGENT (Template Full IntegraIA)
    # ========================================
    # MongoDB persistence for leads, messages, sessions
    mongodb_uri: str = Field(
        default="",
        description="MongoDB connection URI. Example: mongodb+srv://user:pass@cluster.mongodb.net/"
    )
    mongodb_db_name: str = Field(
        default="whatsapp_sales_agent",
        description="MongoDB database name for WhatsApp Sales Agent"
    )
    
    # Melvis (Vector Store for RAG/Knowledge Base)
    melvis_api_url: str = Field(
        default="",
        description="Melvis API base URL for vector search queries"
    )
    melvis_api_key: str = Field(
        default="",
        description="Melvis API key for authentication"
    )
    melvis_collection: str = Field(
        default="kb_sales",
        description="Melvis collection name for sales knowledge base"
    )
    
    # Tavily (Web Search for real-time context)
    tavily_api_key: str = Field(
        default="",
        description="Tavily API key for web search. Get from tavily.com"
    )
    
    # LinkedIn (Lead Enrichment)
    linkedin_api_key: str = Field(
        default="",
        description="LinkedIn API key for lead enrichment (or alternative enrichment service)"
    )
    linkedin_base_url: str = Field(
        default="https://api.linkedin.com/v2",
        description="LinkedIn API base URL (or alternative enrichment service endpoint)"
    )
    
    # Stripe (Payment Checkout)
    stripe_secret_key: str = Field(
        default="",
        description="Stripe secret API key. Get from Stripe dashboard (sk_live_... or sk_test_...)"
    )
    stripe_price_id: str = Field(
        default="",
        description="Stripe Price ID for checkout sessions. Example: price_1ABC123..."
    )
    stripe_success_url: str = Field(
        default="https://dania.agency/gracias",
        description="Redirect URL after successful payment"
    )
    stripe_cancel_url: str = Field(
        default="https://dania.agency/cancelado",
        description="Redirect URL when payment is cancelled"
    )
    
    # Cal.com (Booking/Scheduling)
    calcom_booking_link: str = Field(
        default="https://cal.com/dania-agency/consulta-gratuita",
        description="Cal.com booking link to share with qualified leads"
    )
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Storage
    storage_root: str = "./storage"
    
    # Axon Core Integration
    axon_core_api_base: str = "https://cheque-noticed-wedding-beings.trycloudflare.com"
    axon_core_api_token: str = ""
    axon_core_enabled: bool = True
    
    # Autonomous Agent
    autonomous_agent_architect_enabled: bool = True
    autonomous_agent_review_council_enabled: bool = True  # ✅ Council enabled!
    
    # LLM Router Configuration
    llm_router_enabled: bool = True
    ollama_available: bool = False  # Auto-detected at startup
    
    @property
    def llm_preferences(self) -> dict[str, list[str]]:
        """LLM provider preferences by task type."""
        return {
            "simple": ["ollama", "gemini", "openai"],
            "code": ["gemini", "ollama", "openai"],
            "multimodal": ["gemini"],
            "complex": ["openai", "gemini"],
            "image": ["gemini", "sdxl"]
        }


settings = Settings()
