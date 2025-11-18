import socketio
from loguru import logger
from app.security import verify_token
from app.core.types import TokenPayload


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)


@sio.event
async def connect(sid, environ, auth):
    """Handle WebSocket connection."""
    try:
        if not auth or "token" not in auth:
            logger.warning(f"WebSocket connection rejected: missing token (sid={sid})")
            return False
        
        token = auth["token"]
        token_payload = verify_token(token)
        
        async with sio.session(sid) as session:
            session["user"] = token_payload.sub
            session["role"] = token_payload.role.value
        
        logger.info(f"WebSocket connected: {token_payload.sub} (sid={sid})")
        return True
        
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        return False


@sio.event
async def disconnect(sid):
    """Handle WebSocket disconnection."""
    try:
        async with sio.session(sid) as session:
            user = session.get("user", "unknown")
        logger.info(f"WebSocket disconnected: {user} (sid={sid})")
    except Exception as e:
        logger.error(f"WebSocket disconnect error: {e}")


async def broadcast_event(event_type: str, data: dict):
    """Broadcast event to all connected clients."""
    try:
        await sio.emit(event_type, data)
        logger.debug(f"Broadcast event: {event_type}")
    except Exception as e:
        logger.error(f"Failed to broadcast event: {e}")


async def emit_to_user(user: str, event_type: str, data: dict):
    """Emit event to specific user."""
    try:
        for sid in sio.manager.get_participants("/", None):
            async with sio.session(sid) as session:
                if session.get("user") == user:
                    await sio.emit(event_type, data, room=sid)
                    logger.debug(f"Emitted to user {user}: {event_type}")
    except Exception as e:
        logger.error(f"Failed to emit to user: {e}")
