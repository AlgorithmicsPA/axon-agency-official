from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.core.types import TokenPayload, CatalogResponse, DetectedServices
from app.config import settings
from app.core.detect import load_audit_file, detect_services_from_audit, get_system_capabilities


router = APIRouter(prefix="/api", tags=["catalog"])


_cached_audit = None
_cached_detected = None


def get_detected_services() -> DetectedServices:
    """Get detected services from audit file (cached)."""
    global _cached_audit, _cached_detected
    
    if _cached_detected is None:
        _cached_audit = load_audit_file()
        _cached_detected = detect_services_from_audit(_cached_audit)
    
    return _cached_detected


@router.get("/catalog", response_model=CatalogResponse)
async def get_catalog(current_user: TokenPayload = Depends(get_current_user)):
    """Get system catalog and capabilities."""
    detected = get_detected_services()
    capabilities = get_system_capabilities(detected)
    
    return CatalogResponse(
        version="1.0.0",
        dev_mode=settings.dev_mode,
        audit_loaded=_cached_audit is not None,
        services_detected=detected,
        capabilities=capabilities,
    )
