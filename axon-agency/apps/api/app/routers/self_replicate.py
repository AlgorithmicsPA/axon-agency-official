from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Set
from enum import Enum
import zipfile
import io
import json
import fnmatch
import re
from pathlib import Path
from loguru import logger

from app.services.introspection import IntrospectionService, FileMetrics

router = APIRouter(prefix="/api/self-replicate", tags=["self-replication"])


# Explicit manifests for each variant (allowlist approach)
VARIANT_MANIFESTS = {
    "full": {
        "include_patterns": [
            "apps/api/**/*.py",
            "apps/web/app/**/*.{ts,tsx,js,jsx}",
            "apps/web/components/**/*.{ts,tsx}",
            "apps/web/lib/**/*.ts",
            "apps/web/**/*.{js,css,json}",
            "apps/web/public/**/*",
            "*.md",
            "*.txt",
            "*.toml",
        ],
        "required_files": [
            "apps/api/app/main.py",
            "apps/web/app/layout.tsx",
        ]
    },
    "frontend": {
        "include_patterns": [
            "apps/web/app/**/*.{ts,tsx,js,jsx}",
            "apps/web/components/**/*.{ts,tsx}",
            "apps/web/lib/**/*.ts",
            "apps/web/**/*.{js,css,json}",
            "apps/web/public/**/*",
        ],
        "required_files": [
            "apps/web/app/layout.tsx",
        ]
    },
    "backend": {
        "include_patterns": [
            "apps/api/**/*.py",
        ],
        "required_files": [
            "apps/api/app/main.py",
        ]
    }
}

# Strict blocklist for sensitive/generated files
BLOCKLIST_PATTERNS = {
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".git",
    ".pytest_cache",
    "storage/",
    "logs/",
    "*.db",
    "*.sqlite",
    "*.log",
    ".env",
    ".env.local",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
}


class ReplicaVariant(str, Enum):
    FULL = "full"
    FRONTEND = "frontend"
    BACKEND = "backend"


class ReplicationRequest(BaseModel):
    variant: ReplicaVariant
    name: str


class ReplicationResponse(BaseModel):
    replica_id: str
    variant: str
    files_count: int
    total_loc: int
    bootstrap_instructions: str
    download_url: str


@router.post("/replicate", response_model=ReplicationResponse)
async def replicate_agent(request: ReplicationRequest):
    """
    Create a self-replicating copy of AXON Agency.
    
    Variants:
    - full: Complete AXON Agency (frontend + backend)
    - frontend: Next.js frontend only
    - backend: FastAPI backend only
    """
    
    try:
        introspection = IntrospectionService()
        structure = introspection.scan_repository()
        
        # Get repository root from introspection
        repo_root = introspection.root_path
        
        # Build manifest-based file selection
        selected_files = _build_variant_manifest(structure, request.variant, repo_root)
        
        # Generate bootstrap script
        bootstrap = _generate_bootstrap_script(request.variant, request.name)
        
        replica_id = request.name.lower().replace(' ', '-')
        
        return ReplicationResponse(
            replica_id=replica_id,
            variant=request.variant.value,
            files_count=len(selected_files),
            total_loc=sum(f.lines_of_code for f in selected_files.values()),
            bootstrap_instructions=bootstrap,
            download_url=f"/api/self-replicate/download/{replica_id}?variant={request.variant.value}"
        )
        
    except Exception as e:
        logger.error(f"Replication failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{replica_id}")
async def download_replica(replica_id: str, variant: str):
    """Download self-replicating agent as ZIP file."""
    
    try:
        introspection = IntrospectionService()
        structure = introspection.scan_repository()
        
        # Get repository root dynamically
        repo_root = introspection.root_path
        
        variant_enum = ReplicaVariant(variant)
        selected_files = _build_variant_manifest(structure, variant_enum, repo_root)
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add README
            readme = _generate_readme(replica_id, variant_enum, len(selected_files))
            zip_file.writestr("README.md", readme)
            
            # Add all source files with proper relative paths
            for file_path, metrics in selected_files.items():
                try:
                    full_path = repo_root / file_path
                    if full_path.exists() and full_path.is_file():
                        # Read binary-safe
                        content = full_path.read_bytes()
                        # Write with path relative to repo root
                        relative_path = Path(file_path).as_posix()
                        zip_file.writestr(relative_path, content)
                except Exception as e:
                    logger.warning(f"Could not add {file_path}: {e}")
            
            # Add bootstrap script
            bootstrap_script = _generate_bootstrap_script(variant_enum, replica_id)
            zip_file.writestr("bootstrap.sh", bootstrap_script)
            
            # Add configuration files
            config_files = _generate_config_files(variant_enum, replica_id)
            for path, content in config_files.items():
                zip_file.writestr(path, content)
            
            # Add dependency manifests
            dep_manifests = _generate_dependency_manifests(variant_enum, selected_files, repo_root)
            for path, content in dep_manifests.items():
                zip_file.writestr(path, content)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={replica_id}.zip"}
        )
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variants")
async def list_variants():
    """List available self-replication variants."""
    return {
        "variants": [
            {
                "id": "full",
                "name": "Full Stack Agent",
                "description": "Complete AXON Agency with frontend and backend",
                "includes": ["Next.js Frontend", "FastAPI Backend", "All Features"],
                "estimated_loc": "~8800 lines"
            },
            {
                "id": "frontend",
                "name": "Frontend Only",
                "description": "Next.js UI with API client",
                "includes": ["React Components", "UI Library", "API Integration"],
                "estimated_loc": "~3600 lines"
            },
            {
                "id": "backend",
                "name": "Backend Only",
                "description": "FastAPI backend with all services",
                "includes": ["REST API", "LLM Integration", "Database", "Services"],
                "estimated_loc": "~5200 lines"
            }
        ]
    }


def _is_blocked(file_path: str) -> bool:
    """Check if file matches blocklist patterns."""
    path_str = str(file_path)
    
    for pattern in BLOCKLIST_PATTERNS:
        if pattern.endswith("/"):
            # Directory pattern
            if pattern[:-1] in path_str.split("/"):
                return True
        elif pattern.startswith("*"):
            # Extension pattern
            if path_str.endswith(pattern[1:]):
                return True
        else:
            # Exact match or substring
            if pattern in path_str:
                return True
    
    return False


def _matches_glob_patterns(file_path: str, patterns: List[str]) -> bool:
    """Check if file matches any of the glob patterns."""
    for pattern in patterns:
        # Handle multiple extensions in pattern like *.{ts,tsx}
        if '{' in pattern and '}' in pattern:
            # Extract base pattern and extensions
            base, rest = pattern.split('{')
            extensions, suffix = rest.split('}')
            for ext in extensions.split(','):
                expanded_pattern = f"{base}{ext}{suffix}"
                if _match_pattern(file_path, expanded_pattern):
                    return True
        else:
            # Simple glob pattern
            if _match_pattern(file_path, pattern):
                return True
    return False


def _match_pattern(file_path: str, pattern: str) -> bool:
    """Match file path against pattern supporting ** for recursive directories."""
    # Convert glob to regex properly
    # **/ matches zero or more path components
    # * matches anything except /
    # ? matches single character
    
    regex_parts = []
    i = 0
    while i < len(pattern):
        if pattern[i:i+3] == '**/':
            # **/ means zero or more directories
            regex_parts.append('(?:[^/]+/)*')
            i += 3
        elif pattern[i:i+2] == '**':
            # ** at end means anything
            regex_parts.append('.*')
            i += 2
        elif pattern[i] == '*':
            # * means any chars except /
            regex_parts.append('[^/]*')
            i += 1
        elif pattern[i] == '?':
            # ? means single char
            regex_parts.append('.')
            i += 1
        elif pattern[i] in r'.^$+{}[]|()\\':
            # Escape regex special chars
            regex_parts.append('\\' + pattern[i])
            i += 1
        else:
            regex_parts.append(pattern[i])
            i += 1
    
    regex_pattern = '^' + ''.join(regex_parts) + '$'
    
    try:
        return re.match(regex_pattern, file_path) is not None
    except Exception as e:
        logger.warning(f"Pattern match failed for '{file_path}' against '{pattern}': {e}")
        return False


def _expand_glob_pattern(pattern: str) -> List[str]:
    """Expand patterns with braces like *.{ts,tsx} into multiple patterns."""
    if '{' not in pattern or '}' not in pattern:
        return [pattern]
    
    expanded = []
    base, rest = pattern.split('{', 1)
    extensions, suffix = rest.split('}', 1)
    
    for ext in extensions.split(','):
        expanded.append(f"{base}{ext}{suffix}")
    
    return expanded


def _scan_additional_files(repo_root: Path, patterns: List[str]) -> dict:
    """Scan for additional files matching patterns that IntrospectionService missed."""
    additional = {}
    
    # Extensions already covered by IntrospectionService
    covered_exts = {'.py', '.ts', '.tsx'}
    
    for pattern in patterns:
        # Expand brace patterns
        expanded_patterns = _expand_glob_pattern(pattern)
        
        for exp_pattern in expanded_patterns:
            # Skip if already covered by IntrospectionService
            if any(exp_pattern.endswith(ext) for ext in covered_exts):
                continue
            
            # Handle patterns like apps/web/**/*.json or apps/web/public/**/*
            if '**/' in exp_pattern:
                base_dir, file_pattern = exp_pattern.split('**/', 1)
                search_dir = repo_root / base_dir
                
                if search_dir.exists():
                    # Handle directory-only patterns like apps/web/public/**/*
                    if file_pattern == '*' or file_pattern == '**/*':
                        # Include all files in directory recursively
                        count = 0
                        for file_path in search_dir.rglob('*'):
                            if file_path.is_file():
                                rel_path = str(file_path.relative_to(repo_root))
                                if not _is_blocked(rel_path) and rel_path not in additional:
                                    try:
                                        # Binary-safe read
                                        content = file_path.read_bytes()
                                        additional[rel_path] = FileMetrics(
                                            path=rel_path,
                                            lines_of_code=len(content.splitlines()),
                                            imports=[],
                                            classes=[],
                                            functions=[],
                                            complexity_score=0,
                                            dependencies=set()
                                        )
                                        count += 1
                                    except Exception as e:
                                        logger.warning(f"Could not process {rel_path}: {e}")
                        if count > 0:
                            logger.debug(f"Added {count} files from {base_dir} directory (all files)")
                    
                    # Handle extension-specific patterns like apps/web/**/*.json
                    elif '*.' in file_pattern:
                        ext = file_pattern.split('*.')[-1]
                        if ext and not ext.startswith('*'):
                            # Search for files with this extension recursively
                            count = 0
                            for file_path in search_dir.rglob(f"*.{ext}"):
                                rel_path = str(file_path.relative_to(repo_root))
                                if not _is_blocked(rel_path) and rel_path not in additional:
                                    try:
                                        additional[rel_path] = FileMetrics(
                                            path=rel_path,
                                            lines_of_code=len(file_path.read_text(errors='ignore').splitlines()),
                                            imports=[],
                                            classes=[],
                                            functions=[],
                                            complexity_score=0,
                                            dependencies=set()
                                        )
                                        count += 1
                                    except Exception as e:
                                        logger.warning(f"Could not process {rel_path}: {e}")
                            if count > 0:
                                logger.debug(f"Added {count} *.{ext} files from {base_dir} via rglob")
                            
                            # Also search in base directory itself (not just subdirs)
                            for file_path in search_dir.glob(f"*.{ext}"):
                                if file_path.is_file():
                                    rel_path = str(file_path.relative_to(repo_root))
                                    if not _is_blocked(rel_path) and rel_path not in additional:
                                        try:
                                            additional[rel_path] = FileMetrics(
                                                path=rel_path,
                                                lines_of_code=len(file_path.read_text(errors='ignore').splitlines()),
                                                imports=[],
                                                classes=[],
                                                functions=[],
                                                complexity_score=0,
                                                dependencies=set()
                                            )
                                            logger.debug(f"Added file from base dir: {rel_path}")
                                        except Exception as e:
                                            logger.warning(f"Could not process {rel_path}: {e}")
            # Handle simple patterns like *.md
            elif exp_pattern.startswith('*.'):
                ext = exp_pattern[1:]  # Remove *
                for file_path in repo_root.rglob(f"*{ext}"):
                    rel_path = str(file_path.relative_to(repo_root))
                    if not _is_blocked(rel_path) and rel_path not in additional:
                        try:
                            additional[rel_path] = FileMetrics(
                                path=rel_path,
                                lines_of_code=len(file_path.read_text(errors='ignore').splitlines()),
                                imports=[],
                                classes=[],
                                functions=[],
                                complexity_score=0,
                                dependencies=set()
                            )
                        except Exception as e:
                            logger.warning(f"Could not process {rel_path}: {e}")
    
    return additional


def _build_variant_manifest(structure, variant: ReplicaVariant, repo_root: Path) -> dict:
    """Build file manifest for variant using allowlist glob patterns."""
    selected = {}
    manifest = VARIANT_MANIFESTS[variant.value]
    include_patterns = manifest.get("include_patterns", [])
    
    # Step 1: Filter files from introspection scan using glob patterns
    for path, metrics in structure.files.items():
        # Apply blocklist first (security)
        if _is_blocked(path):
            logger.debug(f"Blocked file: {path}")
            continue
        
        # Check if file matches any include pattern
        if _matches_glob_patterns(path, include_patterns):
            # Verify file exists
            full_path = repo_root / path
            if full_path.exists() and full_path.is_file():
                selected[path] = metrics
            else:
                logger.warning(f"File in structure but not found: {path}")
    
    # Step 2: Scan for additional files not covered by IntrospectionService
    additional_files = _scan_additional_files(repo_root, include_patterns)
    for path, metrics in additional_files.items():
        if path not in selected and _matches_glob_patterns(path, include_patterns):
            selected[path] = metrics
            logger.debug(f"Added additional file: {path}")
    
    # Step 3: Validate required files are present
    for required in manifest.get("required_files", []):
        if required not in selected:
            logger.error(f"Required file missing from manifest: {required}")
            raise ValueError(f"Variant {variant.value} missing required file: {required}")
    
    logger.info(f"Built manifest for {variant.value}: {len(selected)} files")
    return selected


def _generate_bootstrap_script(variant: ReplicaVariant, name: str) -> str:
    """Generate bootstrap installation script."""
    
    if variant == ReplicaVariant.FULL:
        return f"""#!/bin/bash
# Bootstrap script for {name} - Full Stack AXON Agent Replica

set -e

echo "🤖 Bootstrapping AXON Agent: {name}"
echo "Variant: Full Stack (Frontend + Backend)"
echo ""

# Check dependencies
echo "Checking dependencies..."
command -v python3 >/dev/null 2>&1 || {{ echo "Python 3 required"; exit 1; }}
command -v node >/dev/null 2>&1 || {{ echo "Node.js required"; exit 1; }}
command -v npm >/dev/null 2>&1 || {{ echo "npm required"; exit 1; }}

# Backend setup
echo "Setting up backend..."
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..

# Frontend setup
echo "Setting up frontend..."
cd apps/web
npm install
cd ../..

# Create .env files
echo "Creating environment files..."
cat > apps/api/.env << EOF
DATABASE_URL=sqlite:///./agent.db
DEV_MODE=true
EOF

cat > apps/web/.env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
EOF

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "To start the agent:"
echo "  Backend:  cd apps/api && uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080"
echo "  Frontend: cd apps/web && npm run dev"
"""
    
    elif variant == ReplicaVariant.FRONTEND:
        return f"""#!/bin/bash
# Bootstrap script for {name} - Frontend Only

set -e

echo "🤖 Bootstrapping AXON Frontend: {name}"
echo ""

command -v node >/dev/null 2>&1 || {{ echo "Node.js required"; exit 1; }}
command -v npm >/dev/null 2>&1 || {{ echo "npm required"; exit 1; }}

cd apps/web
npm install

cat > .env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
EOF

echo ""
echo "✅ Bootstrap complete!"
echo "Start with: npm run dev"
"""
    
    else:  # BACKEND
        return f"""#!/bin/bash
# Bootstrap script for {name} - Backend Only

set -e

echo "🤖 Bootstrapping AXON Backend: {name}"
echo ""

command -v python3 >/dev/null 2>&1 || {{ echo "Python 3 required"; exit 1; }}

cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cat > .env << EOF
DATABASE_URL=sqlite:///./agent.db
DEV_MODE=true
EOF

echo ""
echo "✅ Bootstrap complete!"
echo "Start with: uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8080"
"""


def _generate_readme(name: str, variant: ReplicaVariant, file_count: int) -> str:
    """Generate README for replicated agent."""
    
    return f"""# {name}

🤖 **Self-Replicating AXON Agent** - Variant: {variant.value.title()}

This is an autonomous AI coding assistant generated via self-replication from AXON Agency.

## Overview

- **Variant**: {variant.value.title()}
- **Files**: {file_count}
- **Features**: Multi-LLM orchestration, Code execution, Self-improvement

## Quick Start

```bash
# Make bootstrap script executable
chmod +x bootstrap.sh

# Run bootstrap
./bootstrap.sh
```

## Features

{'- ✅ Next.js Frontend UI' if variant in [ReplicaVariant.FULL, ReplicaVariant.FRONTEND] else ''}
{'- ✅ FastAPI Backend' if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND] else ''}
{'- ✅ Multi-LLM Support (Ollama, Gemini, OpenAI)' if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND] else ''}
{'- ✅ Code Playground with Docker Sandbox' if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND] else ''}
{'- ✅ Self-Improvement System' if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND] else ''}
{'- ✅ RAG/Training Module' if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND] else ''}

## Architecture

This replica is a {'complete copy' if variant == ReplicaVariant.FULL else 'partial copy'} of the original AXON Agency,
designed to operate autonomously and {'replicate itself' if variant == ReplicaVariant.FULL else 'integrate with backends' if variant == ReplicaVariant.FRONTEND else 'serve frontends'}.

## Configuration

Environment variables are set in:
- Backend: `apps/api/.env`
- Frontend: `apps/web/.env.local`

## Self-Replication

{'This replica can create additional copies of itself using the `/api/self-replicate` endpoint.' if variant == ReplicaVariant.FULL else 'This is a partial replica. For full self-replication capability, use the full-stack variant.'}

---

Generated by AXON Agency Self-Replication System
"""


def _generate_config_files(variant: ReplicaVariant, name: str) -> dict:
    """Generate configuration files for the replica."""
    
    configs = {}
    
    if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND]:
        configs["apps/api/.env.example"] = """# AXON Agent Configuration

# Database
DATABASE_URL=sqlite:///./agent.db

# Development
DEV_MODE=true

# Optional: LLM API Keys
OPENAI_API_KEY=
GEMINI_API_KEY=
"""
    
    if variant in [ReplicaVariant.FULL, ReplicaVariant.FRONTEND]:
        configs["apps/web/.env.local.example"] = """# Frontend Configuration

NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
"""
    
    # Add deployment config
    configs["DEPLOYMENT.md"] = f"""# Deployment Guide for {name}

## Local Development

Follow instructions in README.md

## Production Deployment

### Backend (if included)

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:socket_app --host 0.0.0.0 --port 8080 --workers 4
```

### Frontend (if included)

```bash
cd apps/web
npm run build
npm start
```

## Environment Variables

Set production environment variables according to your deployment platform.

## Docker Support

Coming soon: Containerized deployment with Docker Compose.
"""
    
    return configs


def _generate_dependency_manifests(variant: ReplicaVariant, selected_files: dict, repo_root: Path) -> dict:
    """Generate dependency manifests only if not already in selected_files."""
    manifests = {}
    
    if variant in [ReplicaVariant.FULL, ReplicaVariant.BACKEND]:
        # Only add if not already in manifest
        if "apps/api/requirements.txt" not in selected_files:
            req_file = repo_root / "apps/api/requirements.txt"
            if req_file.exists():
                manifests["apps/api/requirements.txt"] = req_file.read_text()
    
    if variant in [ReplicaVariant.FULL, ReplicaVariant.FRONTEND]:
        # Only add if not already in manifest
        if "apps/web/package.json" not in selected_files:
            pkg_file = repo_root / "apps/web/package.json"
            if pkg_file.exists():
                manifests["apps/web/package.json"] = pkg_file.read_text()
    
    return manifests
