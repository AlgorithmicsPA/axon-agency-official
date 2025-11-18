"""Ayrshare API client for social media publishing."""

import logging
import httpx
import json
from typing import Optional
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RATE_LIMIT_CACHE_PATH = "/tmp/ayrshare_rate_limit_cache.json"


class AyrshareError(Exception):
    """Custom exception for Ayrshare API errors."""
    pass


def parse_rate_limit_headers(headers: dict) -> dict | None:
    """
    Parse Ayrshare rate limit headers.
    
    Headers:
    - x-ratelimit-max: Maximum allowed requests per 5-minute window
    - x-ratelimit-count: Number of requests made in current window
    
    Returns dict: {remaining, limit, count, last_updated}
    """
    try:
        limit = int(headers.get("x-ratelimit-max", 300))
        count = int(headers.get("x-ratelimit-count", 0))
        remaining = max(0, limit - count)
        
        return {
            "remaining": remaining,
            "limit": limit,
            "count": count,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    except (ValueError, TypeError):
        return None


def save_rate_limit_cache(rate_limit_data: dict):
    """Save rate limit info to /tmp cache."""
    try:
        Path(RATE_LIMIT_CACHE_PATH).write_text(json.dumps(rate_limit_data, indent=2))
    except Exception as e:
        logger.warning(f"Failed to save rate limit cache: {e}")


def get_rate_limit_info() -> dict | None:
    """
    Get latest rate limit info from cache.
    
    Returns dict with {remaining, limit, count, last_updated} or None if cache doesn't exist.
    """
    try:
        cache_path = Path(RATE_LIMIT_CACHE_PATH)
        if cache_path.exists():
            return json.loads(cache_path.read_text())
        return None
    except Exception as e:
        logger.warning(f"Failed to read rate limit cache: {e}")
        return None


async def post_to_social(
    api_key: str,
    base_url: str,
    text: str,
    platforms: list[str],
    media_urls: Optional[list[str]] = None,
    schedule_iso: Optional[str] = None,
    profile_key: Optional[str] = None,
) -> dict:
    """
    Publicar contenido en redes sociales vía Ayrshare API.
    
    Args:
        api_key: Ayrshare API key (Bearer token)
        base_url: Base URL de Ayrshare API (ej: https://app.ayrshare.com/api)
        text: Texto del post
        platforms: Lista de plataformas ['twitter', 'facebook', 'instagram']
        media_urls: URLs de imágenes/videos a incluir (opcional)
        schedule_iso: Fecha/hora de publicación programada en ISO 8601 (opcional)
        profile_key: Profile key para multi-perfil (opcional)
    
    Returns:
        dict: Response de Ayrshare API
        {
            "status": "success",
            "id": "ayr-post-id",
            "postIds": {"twitter": "123", "facebook": "456"}
        }
    
    Raises:
        AyrshareError: Si la API retorna error o falla la request
    """
    logger.info(f"Posting to Ayrshare social platforms: {', '.join(platforms)}")
    
    payload = {
        "post": text,
        "platforms": platforms
    }
    
    if media_urls:
        payload["mediaUrls"] = media_urls
    
    if schedule_iso:
        payload["scheduleDate"] = schedule_iso
    
    if profile_key:
        payload["profileKey"] = profile_key
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/post",
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            rate_limit_data = parse_rate_limit_headers(dict(response.headers))
            if rate_limit_data:
                save_rate_limit_cache(rate_limit_data)
            
            logger.info(f"Ayrshare post successful: {data.get('id', 'unknown')}")
            
            return data
    
    except httpx.HTTPStatusError as e:
        rate_limit_data = parse_rate_limit_headers(dict(e.response.headers))
        if rate_limit_data:
            save_rate_limit_cache(rate_limit_data)
        
        error_msg = f"Ayrshare API returned {e.response.status_code}"
        
        try:
            error_data = e.response.json()
            error_msg += f": {error_data.get('message', 'Unknown error')}"
        except:
            error_msg += f": {e.response.text[:200]}"
        
        logger.error(f"Ayrshare API error: {error_msg}")
        raise AyrshareError(error_msg)
    
    except httpx.TimeoutException:
        error_msg = "Ayrshare API request timeout (30s)"
        logger.error(error_msg)
        raise AyrshareError(error_msg)
    
    except Exception as e:
        error_msg = f"Ayrshare API exception: {str(e)[:200]}"
        logger.error(error_msg)
        raise AyrshareError(error_msg)
