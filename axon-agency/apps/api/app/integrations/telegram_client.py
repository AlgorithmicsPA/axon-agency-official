"""Telegram Bot API client for sending messages."""

import httpx
import logging
from typing import Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TelegramError(Exception):
    """Telegram Bot API error."""
    pass


class TelegramResponse(BaseModel):
    """Telegram Bot API response."""
    ok: bool
    result: Optional[dict] = None
    description: Optional[str] = None
    error_code: Optional[int] = None


async def send_to_telegram(
    bot_token: str,
    base_url: str,
    chat_id: str,
    text: str,
    photo_urls: Optional[List[str]] = None,
    parse_mode: str = "HTML"
) -> dict:
    """
    Send message to Telegram chat via Bot API.
    
    Supports:
    - Text-only messages (sendMessage)
    - Single photo with caption (sendPhoto)
    - Multiple photos (sendMediaGroup)
    
    Args:
        bot_token: Telegram bot token from @BotFather
        base_url: API base URL (default: https://api.telegram.org)
        chat_id: Target chat ID (user, group, or channel)
        text: Message text (becomes caption if photo_urls provided)
        photo_urls: Optional list of image URLs to send
        parse_mode: Parsing mode (HTML, Markdown, MarkdownV2)
    
    Returns:
        dict: Telegram API response (ok, result, description, error_code)
    
    Raises:
        TelegramError: If API returns error or HTTP error occurs
    """
    has_media = photo_urls and len(photo_urls) > 0
    
    if not has_media:
        endpoint_method = "sendMessage"
    elif len(photo_urls) == 1:
        endpoint_method = "sendPhoto"
    else:  # len(photo_urls) > 1
        endpoint_method = "sendMediaGroup"
    
    endpoint = f"{base_url}/bot{bot_token}/{endpoint_method}"
    
    if endpoint_method == "sendMediaGroup":
        media_array = []
        for i, photo_url in enumerate(photo_urls):
            media_item = {
                "type": "photo",
                "media": photo_url
            }
            if i == 0:
                media_item["caption"] = text
                media_item["parse_mode"] = parse_mode
            media_array.append(media_item)
        
        payload = {
            "chat_id": chat_id,
            "media": media_array
        }
        logger.info(f"Sending {len(photo_urls)} photos via sendMediaGroup")
        
    elif endpoint_method == "sendPhoto":
        payload = {
            "chat_id": chat_id,
            "photo": photo_urls[0],
            "caption": text,
            "parse_mode": parse_mode
        }
    else:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            truncated_token = f"{bot_token[:8]}..." if len(bot_token) > 8 else "***"
            logger.info(
                f"Sending Telegram {endpoint_method} to chat {chat_id} (token: {truncated_token})"
            )
            
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("ok"):
                error_msg = data.get("description", "Unknown error")
                error_code = data.get("error_code", 0)
                logger.error(f"Telegram API error {error_code}: {error_msg}")
                raise TelegramError(f"Telegram API error {error_code}: {error_msg}")
            
            result = data.get("result")
            if endpoint_method == "sendMediaGroup":
                message_ids = [msg.get("message_id") for msg in result] if isinstance(result, list) else []
                message_id = message_ids[0] if message_ids else None
                logger.info(
                    f"Telegram sendMediaGroup sent successfully. Message IDs: {message_ids}, "
                    f"Media: {len(photo_urls)} photos"
                )
            else:
                message_id = result.get("message_id") if isinstance(result, dict) else None
                logger.info(
                    f"Telegram {endpoint_method} sent successfully. Message ID: {message_id}, "
                    f"Media: {len(photo_urls) if photo_urls else 0} photos"
                )
            return data
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        logger.error(f"Telegram API HTTP error: {error_msg}")
        raise TelegramError(error_msg)
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)[:200]}"
        logger.error(f"Telegram API request error: {error_msg}")
        raise TelegramError(error_msg)
