"""Products/Autopilots catalog endpoint."""

from fastapi import APIRouter, Depends
from typing import List
from app.core.security import get_current_user_optional
from app.core.product_catalog import ProductDefinition, get_available_products, PRODUCT_CATALOG

router = APIRouter()


@router.get("/catalog", response_model=List[ProductDefinition])
async def get_product_catalog(current_user = Depends(get_current_user_optional)):
    """
    Get catalog of available autopilot products.
    
    Returns all products that are currently available (available=True).
    Each product includes:
    - Product type, name, description
    - Channels (WhatsApp, Telegram, Social, etc.)
    - Template module/function (if applicable)
    - Deploy endpoint
    - Required and optional ENV vars
    """
    return get_available_products()


@router.get("/catalog/all", response_model=List[ProductDefinition])
async def get_all_products(current_user = Depends(get_current_user_optional)):
    """
    Get all products including future/unavailable ones.
    Useful for roadmap display.
    """
    return list(PRODUCT_CATALOG.values())
