from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from loguru import logger
from app.services.introspection import IntrospectionService, CodeStructure


router = APIRouter(prefix="/api/self-improve", tags=["self-improvement"])


class RepoAnalysisResponse(BaseModel):
    """Repository analysis result."""
    total_files: int
    total_loc: int
    language_breakdown: Dict[str, int]
    top_files_by_loc: List[Dict[str, Any]]
    improvement_opportunities: List[Dict[str, Any]]


class ImprovementOpportunity(BaseModel):
    """Single improvement suggestion."""
    type: str
    severity: str
    file: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/analyze", response_model=RepoAnalysisResponse)
async def analyze_repository():
    """Analyze the agent's own codebase and find improvement opportunities."""
    try:
        logger.info("Starting repository introspection")
        
        introspection = IntrospectionService()
        structure = introspection.scan_repository()
        opportunities = introspection.find_improvement_opportunities(structure)
        
        # Get top 10 largest files
        top_files = sorted(
            [
                {
                    "path": path,
                    "loc": metrics.lines_of_code,
                    "complexity": metrics.complexity_score,
                    "functions": len(metrics.functions),
                    "classes": len(metrics.classes)
                }
                for path, metrics in structure.files.items()
            ],
            key=lambda x: x["loc"],
            reverse=True
        )[:10]
        
        return RepoAnalysisResponse(
            total_files=structure.file_count,
            total_loc=structure.total_loc,
            language_breakdown=structure.language_breakdown,
            top_files_by_loc=top_files,
            improvement_opportunities=opportunities
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structure", response_model=Dict[str, Any])
async def get_code_structure():
    """Get detailed code structure including dependency graph."""
    try:
        introspection = IntrospectionService()
        structure = introspection.scan_repository()
        
        # Convert to serializable format
        files_data = {}
        for path, metrics in structure.files.items():
            files_data[path] = {
                "loc": metrics.lines_of_code,
                "imports": metrics.imports,
                "classes": metrics.classes,
                "functions": metrics.functions,
                "complexity": metrics.complexity_score,
                "dependencies": list(metrics.dependencies)
            }
        
        dep_graph = {
            path: list(deps) 
            for path, deps in structure.dependency_graph.items()
        }
        
        return {
            "files": files_data,
            "dependency_graph": dep_graph,
            "stats": {
                "total_files": structure.file_count,
                "total_loc": structure.total_loc,
                "languages": structure.language_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get code structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_path:path}", response_model=Dict[str, Any])
async def get_file_analysis(file_path: str):
    """Get detailed analysis of a specific file."""
    try:
        introspection = IntrospectionService()
        structure = introspection.scan_repository()
        
        # File paths are now relative, so use directly
        if file_path not in structure.files:
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        metrics = structure.files[file_path]
        dependencies = structure.dependency_graph.get(file_path, set())
        
        # Find files that depend on this file
        dependents = [
            path for path, deps in structure.dependency_graph.items()
            if file_path in deps
        ]
        
        return {
            "path": metrics.path,
            "loc": metrics.lines_of_code,
            "complexity": metrics.complexity_score,
            "imports": metrics.imports,
            "classes": metrics.classes,
            "functions": metrics.functions,
            "dependencies": list(dependencies),
            "dependents": dependents,
            "external_deps": list(metrics.dependencies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
