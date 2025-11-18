"""Code playground router - execute code safely in Docker containers."""

import logging
import asyncio
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class CodeExecuteRequest(BaseModel):
    """Code execution request."""
    code: str
    language: str  # python, javascript, typescript, go, rust
    stdin: str | None = None
    timeout: int = 30  # seconds


class CodeExecuteResponse(BaseModel):
    """Code execution response."""
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float  # seconds
    warnings: list[str] = []


@router.post("/execute", response_model=CodeExecuteResponse)
async def execute_code(request: CodeExecuteRequest):
    """Execute code in a secure Docker container.
    
    Security features:
    - Isolated Docker container (ephemeral)
    - CPU/Memory limits
    - Network restrictions
    - Timeout enforcement
    - No filesystem access
    """
    try:
        if request.language not in ["python", "javascript", "typescript", "go", "rust", "bash"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}"
            )
        
        # Generate unique container name
        container_name = f"axon-exec-{uuid.uuid4().hex[:8]}"
        
        # Select Docker image and command
        use_stdin = False
        code_input = None
        warnings = []
        
        if request.language == "python":
            image = "python:3.11-slim"
            cmd = ["python", "-c", request.code]
            
        elif request.language in ["javascript", "typescript"]:
            image = "node:20-slim"
            if request.language == "typescript":
                warning_msg = "TypeScript executed as JavaScript (no transpilation). TypeScript-specific syntax may cause runtime errors."
                logger.warning(warning_msg)
                warnings.append(warning_msg)
            cmd = ["node", "-e", request.code]
            
        elif request.language == "go":
            image = "golang:1.21-alpine"
            cmd = ["sh", "-c", "cat > /tmp/main.go && cd /tmp && go run main.go"]
            use_stdin = True
            code_input = request.code
            
        elif request.language == "rust":
            image = "rust:1.75-slim"
            cmd = ["sh", "-c", "cat > /tmp/main.rs && rustc /tmp/main.rs -o /tmp/prog && /tmp/prog"]
            use_stdin = True
            code_input = request.code
            
        elif request.language == "bash":
            image = "bash:5.2-alpine"
            cmd = ["bash", "-c", request.code]
            
        else:
            raise HTTPException(status_code=400, detail="Language not implemented")
        
        # Build docker run command with security limits
        docker_cmd = [
            "docker", "run",
            "--rm",  # Auto-remove after execution
            "--name", container_name,
            "--cpus", "1.0",  # Limit to 1 CPU
            "--memory", "512m",  # 512MB RAM limit
            "--network", "none",  # No network access
            "--read-only",  # Read-only filesystem
            "--tmpfs", "/tmp:rw,size=100m,mode=1777",  # Writable /tmp
            "-i",  # Interactive for stdin
            image
        ] + cmd
        
        # Execute with timeout
        import time
        start_time = time.time()
        
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Determine what to send to stdin
            stdin_data = None
            if use_stdin and code_input:
                stdin_data = code_input.encode()
            elif request.stdin:
                stdin_data = request.stdin.encode()
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=stdin_data),
                timeout=request.timeout
            )
            
            execution_time = time.time() - start_time
            
            return CodeExecuteResponse(
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=process.returncode or 0,
                execution_time=execution_time,
                warnings=warnings
            )
            
        except asyncio.TimeoutError:
            # Kill container if timeout
            await asyncio.create_subprocess_exec(
                "docker", "kill", container_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            raise HTTPException(
                status_code=408,
                detail=f"Execution timeout after {request.timeout}s"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def list_languages():
    """List supported languages and their versions."""
    return {
        "languages": {
            "python": {
                "version": "3.11",
                "image": "python:3.11-slim",
                "extensions": [".py"]
            },
            "javascript": {
                "version": "Node 20",
                "image": "node:20-slim",
                "extensions": [".js", ".mjs"]
            },
            "typescript": {
                "version": "Node 20 (executed as JS, no transpilation)",
                "image": "node:20-slim",
                "extensions": [".ts"],
                "note": "TypeScript syntax may cause runtime errors"
            },
            "go": {
                "version": "1.21",
                "image": "golang:1.21-alpine",
                "extensions": [".go"]
            },
            "rust": {
                "version": "1.75",
                "image": "rust:1.75-slim",
                "extensions": [".rs"]
            },
            "bash": {
                "version": "5.2",
                "image": "bash:5.2-alpine",
                "extensions": [".sh"]
            }
        }
    }
