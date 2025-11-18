from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload
from app.config import settings
from app.security import require_admin
from app.adapters.tunnels_cloudflared import CloudflaredAdapter
from app.adapters.tunnels_tailscale import TailscaleAdapter
from loguru import logger


router = APIRouter(prefix="/api", tags=["tunnels"])


class TunnelStatus(BaseModel):
    name: str
    type: str
    active: bool
    details: Dict[str, Any] = {}


class TunnelsStatusResponse(BaseModel):
    tunnels: List[TunnelStatus]


@router.get("/tunnels/status", response_model=TunnelsStatusResponse)
async def get_tunnels_status(
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get status of tunnel services."""
    tunnels = []
    
    try:
        cf_adapter = CloudflaredAdapter(settings.cf_service_name)
        cf_status = await cf_adapter.get_status()
        tunnels.append(TunnelStatus(
            name="cloudflared",
            type="cloudflare",
            active=cf_status.get("active", False),
            details=cf_status,
        ))
    except Exception as e:
        logger.warning(f"Cloudflared status error: {e}")
        tunnels.append(TunnelStatus(
            name="cloudflared",
            type="cloudflare",
            active=False,
            details={"error": str(e)},
        ))
    
    try:
        ts_adapter = TailscaleAdapter(settings.tailscale_service_name)
        ts_status = await ts_adapter.get_status()
        tunnels.append(TunnelStatus(
            name="tailscale",
            type="tailscale",
            active=ts_status.get("active", False),
            details=ts_status,
        ))
    except Exception as e:
        logger.warning(f"Tailscale status error: {e}")
        tunnels.append(TunnelStatus(
            name="tailscale",
            type="tailscale",
            active=False,
            details={"error": str(e)},
        ))
    
    return TunnelsStatusResponse(tunnels=tunnels)


class TunnelActionRequest(BaseModel):
    tunnel: str
    action: str


@router.post("/tunnels/action")
async def tunnel_action(
    request: TunnelActionRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Execute action on tunnel (restart)."""
    require_admin(current_user)
    
    if request.action not in ["restart", "status"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        if request.tunnel == "cloudflared":
            adapter = CloudflaredAdapter(settings.cf_service_name)
            result = await adapter.restart() if request.action == "restart" else await adapter.get_status()
        elif request.tunnel == "tailscale":
            adapter = TailscaleAdapter(settings.tailscale_service_name)
            result = await adapter.restart() if request.action == "restart" else await adapter.get_status()
        else:
            raise HTTPException(status_code=400, detail="Invalid tunnel name")
        
        return {"message": f"Action {request.action} executed", "result": result}
        
    except Exception as e:
        logger.error(f"Tunnel action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
