import psutil
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.core.types import TokenPayload, MetricsSnapshot
from loguru import logger


router = APIRouter(prefix="/api", tags=["metrics"])


def get_gpu_metrics():
    """Get GPU metrics using nvidia-smi if available."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                parts = output.split(",")
                return {
                    "utilization": float(parts[0].strip()),
                    "temperature": float(parts[1].strip()),
                }
    except Exception as e:
        logger.debug(f"GPU metrics not available: {e}")
    
    return None


@router.get("/metrics", response_model=MetricsSnapshot)
async def get_metrics(
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get real-time system metrics."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    
    mem = psutil.virtual_memory()
    memory_percent = mem.percent
    memory_available_mb = mem.available / (1024 * 1024)
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    disk_free_gb = disk.free / (1024 * 1024 * 1024)
    
    uptime_seconds = psutil.boot_time()
    uptime = psutil.time.time() - uptime_seconds
    
    load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
    
    gpu_data = get_gpu_metrics()
    
    return MetricsSnapshot(
        timestamp=datetime.utcnow().isoformat() + "Z",
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        memory_available_mb=memory_available_mb,
        disk_percent=disk_percent,
        disk_free_gb=disk_free_gb,
        uptime_seconds=uptime,
        gpu_utilization=gpu_data["utilization"] if gpu_data else None,
        gpu_temp=gpu_data["temperature"] if gpu_data else None,
        load_average=list(load_avg) if load_avg else None,
    )
