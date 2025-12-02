"""AXON Agency API - Main application entry point."""

import logging
import socketio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.security import validate_production_security
from app.routers import (
    health, catalog, metrics, auth, agent,
    media, posts, conversations, integrations,
    autopilots, rag, campaigns, services, axon_core,
    memory, training, evaluation, llm, playground, projects, self_improve, improvement_jobs, self_replicate, learning, autonomous, meta_agent, prompt, factory, orders, tenants, admin, leads, products
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting AXON Agency API...")
    
    # CRITICAL WARNING if dev_mode is active
    if settings.dev_mode:
        logger.critical("=" * 80)
        logger.critical("⚠️  SECURITY WARNING: DEV_MODE IS ENABLED  ⚠️")
        logger.critical("=" * 80)
        logger.critical("Authentication bypass is ACTIVE - API endpoints allow unauthenticated access!")
        logger.critical("This mode should NEVER be enabled in production environments.")
        logger.critical("Set DEV_MODE=false in environment variables to disable.")
        logger.critical("=" * 80)
    
    validate_production_security(settings)
    create_db_and_tables()
    
    storage_path = Path(settings.storage_root)
    storage_path.mkdir(exist_ok=True)
    (storage_path / "media").mkdir(exist_ok=True)
    (storage_path / "drafts").mkdir(exist_ok=True)
    (storage_path / "published").mkdir(exist_ok=True)
    (storage_path / "uploads").mkdir(exist_ok=True)
    (storage_path / "vectors").mkdir(exist_ok=True)
    (storage_path / "learning").mkdir(exist_ok=True)
    (storage_path / "governance").mkdir(exist_ok=True)
    
    # Initialize learning service
    from app.routers.learning import initialize_learning_service
    try:
        await initialize_learning_service()
        logger.info("Learning service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize learning service: {e}")
    
    logger.info(f"API ready on {settings.bind}:{settings.port}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AXON Agency API",
    description="Full-stack IA Agency Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.allowed_origins,
    logger=False,
    engineio_logger=False
)

storage_path = Path(settings.storage_root)
storage_path.mkdir(exist_ok=True)
(storage_path / "media").mkdir(exist_ok=True)
(storage_path / "drafts").mkdir(exist_ok=True)
(storage_path / "published").mkdir(exist_ok=True)

app.mount("/preview", StaticFiles(directory=settings.storage_root + "/drafts"), name="preview")
app.mount("/site", StaticFiles(directory=settings.storage_root + "/published"), name="site")
app.mount("/media", StaticFiles(directory=settings.storage_root + "/media"), name="media")

app.include_router(health.router, tags=["Health"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(autopilots.router, prefix="/api/autopilots", tags=["Autopilots"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(axon_core.router, tags=["Axon Core"])
app.include_router(memory.router, prefix="/api/agents/memory", tags=["Memory"])
app.include_router(training.router, prefix="/api/agents/train", tags=["Training"])
app.include_router(evaluation.router, prefix="/api/eval", tags=["Evaluation"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM"])
app.include_router(playground.router, prefix="/api/code", tags=["Playground"])
app.include_router(projects.router, tags=["Projects"])
app.include_router(self_improve.router, tags=["Self-Improvement"])
app.include_router(improvement_jobs.router, prefix="/api/improve", tags=["Improvement Jobs"])
app.include_router(self_replicate.router, tags=["Self-Replication"])
app.include_router(learning.router, tags=["Learning"])
app.include_router(autonomous.router, tags=["Autonomous Agent"])
app.include_router(meta_agent.router, tags=["Meta Agent"])
app.include_router(prompt.router, tags=["Prompt Engineering"])
app.include_router(factory.router, prefix="/api/factory", tags=["Factory"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])

socket_app = socketio.ASGIApp(sio, app)


@sio.event
async def connect(sid, environ, auth):
    """Handle WebSocket connection."""
    token = auth.get("token") if auth else None
    if not token and settings.dev_mode:
        logger.warning(f"WebSocket connected without token (dev mode): {sid}")
        await sio.save_session(sid, {"user": "dev", "role": "admin"})
        return
    
    logger.info(f"WebSocket connected: {sid}")


@sio.event
async def disconnect(sid):
    """Handle WebSocket disconnection."""
    logger.info(f"WebSocket disconnected: {sid}")


@sio.on("chat:user")
async def handle_chat_user(sid, data):
    """Handle chat message from user."""
    from app.providers.openai import openai_chat_stream
    
    text = data.get("text", "")
    session_id = data.get("session_id", sid)
    
    logger.info(f"Chat from {sid}: {text[:50]}...")
    
    try:
        async for chunk in openai_chat_stream([{"role": "user", "content": text}]):
            await sio.emit("chat:assistant", {"text": chunk, "session_id": session_id}, room=sid)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await sio.emit("chat:error", {"error": str(e)}, room=sid)
