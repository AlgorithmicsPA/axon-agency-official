"""System metrics endpoints."""

import psutil
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/metrics")
async def get_metrics(current_user = Depends(get_current_user)):
    """Get system metrics (requires authentication)."""
    return {
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count()
        },
        "memory": {
            "percent": psutil.virtual_memory().percent,
            "used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "total_mb": psutil.virtual_memory().total / 1024 / 1024
        },
        "disk": {
            "percent": psutil.disk_usage("/").percent,
            "used_gb": psutil.disk_usage("/").used / 1024 / 1024 / 1024,
            "total_gb": psutil.disk_usage("/").total / 1024 / 1024 / 1024
        }
    }
