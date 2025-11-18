from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, TypeVar
import json
import zipfile
import io
from pathlib import Path

from app.providers.gemini import gemini_chat
from app.providers.openai import openai_chat
from app.core.config import settings

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectRequirements(BaseModel):
    name: str
    description: str
    stack: str
    features: List[str]
    additional_notes: Optional[str] = None


class GeneratedFile(BaseModel):
    path: str
    content: str
    description: str


class FileDescriptor(BaseModel):
    """File description in project plan."""
    path: str = Field(min_length=1, description="Relative file path (no leading / or ..)")
    purpose: str = Field(description="What this file does")


class ProjectPlan(BaseModel):
    """Validated project plan from LLM."""
    architecture: str
    file_structure: List[FileDescriptor] = Field(description="List of files to generate")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    key_decisions: List[str] = Field(default_factory=list)


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    files: List[GeneratedFile]
    dependencies: Dict[str, List[str]]
    instructions: str
    setup_commands: List[str]


class ProjectTemplate(BaseModel):
    id: str
    name: str
    description: str
    stack: str
    features: List[str]
    icon: str


TEMPLATES = [
    {
        "id": "fastapi-rest",
        "name": "FastAPI REST API",
        "description": "Production-ready REST API with FastAPI, SQLAlchemy, and JWT auth",
        "stack": "Python/FastAPI",
        "features": ["REST API", "Database", "Authentication", "CORS"],
        "icon": "⚡"
    },
    {
        "id": "nextjs-fullstack",
        "name": "Next.js Full-Stack",
        "description": "Complete web app with Next.js 15, TypeScript, Tailwind CSS",
        "stack": "TypeScript/Next.js",
        "features": ["Frontend", "API Routes", "Database", "Styling"],
        "icon": "🚀"
    },
    {
        "id": "react-spa",
        "name": "React SPA",
        "description": "Single-page application with React, Vite, and React Router",
        "stack": "TypeScript/React",
        "features": ["Frontend", "Routing", "State Management"],
        "icon": "⚛️"
    },
    {
        "id": "express-api",
        "name": "Express.js API",
        "description": "Node.js backend with Express, PostgreSQL, and authentication",
        "stack": "JavaScript/Express",
        "features": ["REST API", "Database", "Authentication"],
        "icon": "🟢"
    },
    {
        "id": "python-cli",
        "name": "Python CLI Tool",
        "description": "Command-line tool with Click, rich output, and config management",
        "stack": "Python/CLI",
        "features": ["CLI", "Config", "Logging"],
        "icon": "🐍"
    },
    {
        "id": "discord-bot",
        "name": "Discord Bot",
        "description": "Discord bot with discord.py, commands, and slash commands",
        "stack": "Python/Discord",
        "features": ["Bot", "Commands", "Events"],
        "icon": "🤖"
    }
]


@router.get("/templates")
async def list_templates():
    """Get list of available project templates"""
    return {"templates": TEMPLATES}


@router.post("/generate", response_model=ProjectResponse)
async def generate_project(requirements: ProjectRequirements):
    """
    Generate a complete project from requirements.
    
    Uses multi-step LLM orchestration:
    1. Analyze requirements and create project plan
    2. Generate file structure
    3. Generate code for each file
    4. Create setup instructions
    """
    
    try:
        # Select LLM provider
        provider_name, chat_func = _get_llm_provider()
        
        # Step 1: Create project plan with LLM
        system_msg = """You are an expert software architect specializing in production-ready code generation.
Your responses must be valid JSON only, no markdown formatting or explanations.
Follow best practices, use proper error handling, and write clean, maintainable code."""

        plan_prompt = f"""Create a complete project plan for:

Project: {requirements.name}
Description: {requirements.description}
Stack: {requirements.stack}
Required Features: {', '.join(requirements.features)}
{f'Notes: {requirements.additional_notes}' if requirements.additional_notes else ''}

Return ONLY valid JSON (no markdown, no explanations):
{{
  "architecture": "Brief overview of system design",
  "file_structure": [
    {{"path": "relative/path/file.ext", "purpose": "What this file does"}}
  ],
  "dependencies": {{
    "python": ["package1"],
    "npm": ["package1"]
  }},
  "key_decisions": ["Design decision 1", "Decision 2"]
}}

Include ALL necessary files for a complete, working project. Be comprehensive."""

        plan_response = await chat_func([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": plan_prompt}
        ])
        
        # Robust JSON extraction with validation
        plan = _extract_and_validate_json(plan_response, ProjectPlan)
        
        # Step 2: Generate code for each file
        generated_files = []
        total_files = len(plan.file_structure)
        
        # System message for code generation (different from planning)
        code_system_msg = """You are an expert programmer. Generate clean, production-ready code.
Return ONLY the raw code content - no markdown formatting, no explanations, no JSON.
Follow best practices, include proper error handling, and write maintainable code."""
        
        for idx, file_info in enumerate(plan.file_structure, 1):
            file_path = file_info.path
            file_purpose = file_info.purpose
            
            code_prompt = f"""Generate production-ready code for file {idx}/{total_files}:

Project Context:
- Name: {requirements.name}
- Description: {requirements.description}
- Stack: {requirements.stack}
- Architecture: {plan.architecture}

This File:
- Path: {file_path}
- Purpose: {file_purpose}

Requirements:
- Follow {requirements.stack} best practices
- Include proper error handling and validation
- Add clear, helpful comments
- Use type hints/annotations
- Make it secure, performant, and maintainable
- Integrate properly with other project files

Return ONLY the file content, no markdown formatting, no explanations."""

            code_response = await chat_func([
                {"role": "system", "content": code_system_msg},
                {"role": "user", "content": code_prompt}
            ])
            
            # Clean up code response
            code = _clean_code_response(code_response)
            
            generated_files.append(GeneratedFile(
                path=file_path,
                content=code,
                description=file_purpose
            ))
        
        # Step 3: Generate setup instructions
        setup_prompt = f"""Create setup instructions for:

Project: {requirements.name}
Stack: {requirements.stack}
Dependencies: {json.dumps(plan.dependencies)}
Files Generated: {len(generated_files)}

Return ONLY valid JSON:
{{
  "setup_commands": ["command1", "command2"],
  "instructions": "Clear step-by-step setup guide with all necessary steps"
}}"""

        setup_response = await chat_func([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": setup_prompt}
        ])
        
        class SetupInfo(BaseModel):
            setup_commands: List[str]
            instructions: str
        
        setup = _extract_and_validate_json(setup_response, SetupInfo)
        
        # Return complete project
        return ProjectResponse(
            project_id=requirements.name.lower().replace(' ', '-'),
            name=requirements.name,
            files=generated_files,
            dependencies=plan.dependencies,
            instructions=setup.instructions,
            setup_commands=setup.setup_commands
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")


@router.post("/generate/{project_id}/download")
async def download_project_zip(project_id: str, project: ProjectResponse):
    """Download generated project as ZIP file with proper directory structure."""
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add README
        readme_content = f"""# {project.name}

{project.instructions}

## Setup Commands

```bash
{chr(10).join(project.setup_commands)}
```

## Dependencies

{json.dumps(project.dependencies, indent=2)}

## Files Generated

{len(project.files)} files in this project.
"""
        zip_file.writestr("README.md", readme_content)
        
        # Add all generated files with sanitized paths
        for file in project.files:
            safe_path = _sanitize_file_path(file.path)
            zip_file.writestr(safe_path, file.content)
        
        # Add dependency files
        if "python" in project.dependencies:
            requirements = "\n".join(project.dependencies["python"])
            zip_file.writestr("requirements.txt", requirements)
        
        if "npm" in project.dependencies:
            package_json = {
                "name": project_id,
                "version": "1.0.0",
                "dependencies": {pkg: "latest" for pkg in project.dependencies["npm"]}
            }
            zip_file.writestr("package.json", json.dumps(package_json, indent=2))
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project_id}.zip"}
    )


from typing import TypeVar

T = TypeVar('T', bound=BaseModel)

def _extract_and_validate_json(response: str, model: type[T]) -> T:
    """Extract JSON from LLM response and validate with Pydantic model."""
    # Try to find JSON block
    json_start = response.find('{')
    json_end = response.rfind('}') + 1
    
    if json_start == -1 or json_end == 0:
        raise HTTPException(
            status_code=500,
            detail="LLM response did not contain valid JSON"
        )
    
    json_str = response[json_start:json_end]
    
    try:
        data = json.loads(json_str)
        return model(**data)  # type: ignore
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON from LLM: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid data structure from LLM: {str(e)}"
        )


def _sanitize_file_path(file_path: str) -> str:
    """Sanitize file path to prevent directory traversal attacks."""
    from pathlib import PurePosixPath
    
    # Remove leading slashes and resolve .. components
    path = PurePosixPath(file_path)
    
    # Get all parts and filter out dangerous ones
    safe_parts = [p for p in path.parts if p != '..' and p != '.' and p != '/']
    
    # Reconstruct safe path
    if not safe_parts:
        return "unnamed_file.txt"
    
    return str(PurePosixPath(*safe_parts))


def _clean_code_response(response: str) -> str:
    """Remove markdown formatting from code response."""
    code = response.strip()
    
    # Remove markdown code blocks
    if code.startswith('```'):
        lines = code.split('\n')
        # Remove first line (```language) and last line (```)
        if len(lines) > 2:
            code = '\n'.join(lines[1:-1])
    
    return code.strip()


def _get_llm_provider():
    """Get the best available LLM provider for code generation"""
    # Prefer OpenAI for code generation quality
    if settings.openai_api_key:
        return ("openai", openai_chat)
    # Fallback to Gemini
    elif settings.gemini_api_key:
        return ("gemini", gemini_chat)
    else:
        raise HTTPException(status_code=503, detail="No LLM provider available")
