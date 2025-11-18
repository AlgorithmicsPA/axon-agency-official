import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socketio
from loguru import logger

from app.config import settings
from app.core.detect import load_audit_file, detect_services_from_audit
from app.ws import sio
from app.routers import health, catalog, commands, files, services, flows, llm, tunnels, metrics
from app.security import create_access_token, Role


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

logger.add(
    "logs/axon-core.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("Axon Core Backend - Starting")
    logger.info("=" * 60)
    logger.info(f"Version: 1.0.0")
    logger.info(f"DEV_MODE: {settings.dev_mode}")
    logger.info(f"PRODUCTION_MODE: {settings.production_mode}")
    logger.info(f"Bind: {settings.bind}:{settings.port}")
    
    if settings.production_mode:
        if settings.jwt_secret == "changeme":
            logger.critical("FATAL: Cannot start in PRODUCTION_MODE with default JWT_SECRET!")
            logger.critical("Set a secure JWT_SECRET in .env file")
            raise RuntimeError("Production mode requires custom JWT_SECRET")
        
        if settings.dev_mode:
            logger.critical("FATAL: Cannot start in PRODUCTION_MODE with DEV_MODE enabled!")
            logger.critical("Set DEV_MODE=false in .env file")
            raise RuntimeError("Production mode cannot run with DEV_MODE enabled")
        
        logger.info("✓ Production security checks passed")
    else:
        if settings.jwt_secret == "changeme":
            logger.warning("⚠️  JWT_SECRET is using default value (acceptable for development)")
        
        if settings.dev_mode:
            logger.warning("⚠️  DEV_MODE is ENABLED - /api/token/dev endpoint is exposed (acceptable for development)")
    
    audit_data = load_audit_file()
    if audit_data:
        logger.info("✓ axon88_audit.json loaded successfully")
        detected = detect_services_from_audit(audit_data)
        logger.info(f"Detected services: {detected.model_dump()}")
    else:
        logger.warning("⚠ axon88_audit.json not found or failed to load")
    
    logger.info("=" * 60)
    
    yield
    
    logger.info("Axon Core Backend - Shutting down")


app = FastAPI(
    title="Axon Core API",
    description="Backend productivo para gestión de infraestructura Axon 88",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(commands.router)
app.include_router(files.router)
app.include_router(services.router)
app.include_router(flows.router)
app.include_router(llm.router)
app.include_router(tunnels.router)
app.include_router(metrics.router)


if settings.dev_mode:
    @app.post("/api/token/dev")
    async def get_dev_token(username: str = "dev-admin"):
        """Development-only endpoint to get JWT token."""
        token = create_access_token(username, Role.ADMIN)
        logger.warning(f"DEV TOKEN generated for: {username}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "admin",
            "username": username,
        }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


sio_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path="/ws/socket.io",
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:sio_app",
        host=settings.bind,
        port=settings.port,
        reload=settings.dev_mode,
        log_level="info",
    )
