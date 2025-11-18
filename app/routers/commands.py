import asyncio
import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.core.types import TokenPayload, CommandTask, CommandStatus
from app.core.utils import is_command_allowed, sanitize_command, write_audit_log
from app.config import settings
from app.ws import broadcast_event
from app.security import require_admin
from loguru import logger


router = APIRouter(prefix="/api", tags=["commands"])


tasks: Dict[str, CommandTask] = {}


class CommandRequest(BaseModel):
    cmd: str


class CommandResponse(BaseModel):
    task_id: str
    status: CommandStatus
    message: str


@router.post("/commands/run", response_model=CommandResponse)
async def run_command(
    request: CommandRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Execute a whitelisted command with streaming logs."""
    require_admin(current_user)
    
    try:
        sanitized_cmd = sanitize_command(request.cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not is_command_allowed(sanitized_cmd, settings.allowed_commands_list):
        raise HTTPException(
            status_code=403,
            detail=f"Command not allowed. Whitelist: {settings.allowed_commands_list}"
        )
    
    task_id = str(uuid.uuid4())
    task = CommandTask(
        task_id=task_id,
        cmd=sanitized_cmd,
        status=CommandStatus.PENDING,
        started_at=datetime.utcnow().isoformat() + "Z",
    )
    tasks[task_id] = task
    
    write_audit_log(
        "command_run",
        current_user.sub,
        {"task_id": task_id, "cmd": sanitized_cmd},
        settings.audit_log_path,
    )
    
    asyncio.create_task(execute_command(task_id, sanitized_cmd))
    
    return CommandResponse(
        task_id=task_id,
        status=CommandStatus.PENDING,
        message="Command queued for execution",
    )


async def execute_command(task_id: str, cmd: str):
    """Execute command and stream output via WebSocket."""
    task = tasks[task_id]
    task.status = CommandStatus.RUNNING
    
    try:
        await broadcast_event("command_started", {"task_id": task_id, "cmd": cmd})
        
        process = await asyncio.create_subprocess_shell(
            f"/bin/bash -lc '{cmd}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            output = line.decode().rstrip()
            await broadcast_event("command_output", {
                "task_id": task_id,
                "output": output,
            })
        
        await process.wait()
        
        task.status = CommandStatus.COMPLETED if process.returncode == 0 else CommandStatus.FAILED
        task.exit_code = process.returncode
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        
        await broadcast_event("command_completed", {
            "task_id": task_id,
            "exit_code": process.returncode,
            "status": task.status.value,
        })
        
        logger.info(f"Command completed: {task_id} (exit={process.returncode})")
        
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        task.status = CommandStatus.FAILED
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        
        await broadcast_event("command_failed", {
            "task_id": task_id,
            "error": str(e),
        })


@router.get("/commands/{task_id}", response_model=CommandTask)
async def get_command_status(
    task_id: str,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get command task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]
