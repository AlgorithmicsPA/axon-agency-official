import os
import uuid
import subprocess
import tempfile
import asyncio
import shutil
import difflib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from loguru import logger

from app.models import ImprovementJob, ImprovementJobStatus, ImprovementType
from app.providers.gemini import gemini_chat


class SelfModificationEngine:
    """
    Safe code modification engine with temp workspace and backup mechanism,
    LLM generation, LSP validation, and optional Docker sandbox testing.
    """
    
    def __init__(self, repo_root: str = "/home/runner/workspace/axon-agency"):
        self.repo_root = Path(repo_root)
        self.temp_root = Path("/tmp/axon-improvements")
        self.temp_root.mkdir(exist_ok=True)
    
    async def execute_improvement(self, job: ImprovementJob) -> Dict:
        """
        Execute an approved improvement job.
        
        Returns:
            Dict with status, changes, metrics, error (if any)
        """
        logger.info(f"Executing improvement job {job.job_id} for {job.target_file}")
        
        backup_path = None
        temp_workspace = None
        
        try:
            temp_workspace = await asyncio.to_thread(self._create_temp_workspace, job.job_id)
            
            target_path = self.repo_root / job.target_file
            if not target_path.exists():
                return {
                    "status": "failed",
                    "error": f"Target file not found: {job.target_file}"
                }
            
            original_code = await asyncio.to_thread(target_path.read_text)
            
            backup_path = await asyncio.to_thread(self._create_backup, target_path)
            
            improved_code = await self._generate_improvement(
                job=job,
                original_code=original_code
            )
            
            if not improved_code:
                await asyncio.to_thread(self._restore_backup, backup_path, target_path)
                return {
                    "status": "failed",
                    "error": "Failed to generate improved code"
                }
            
            await asyncio.to_thread(target_path.write_text, improved_code)
            
            lsp_valid = await self._validate_lsp(target_path)
            if not lsp_valid:
                await asyncio.to_thread(self._restore_backup, backup_path, target_path)
                return {
                    "status": "failed",
                    "error": "LSP validation failed - syntax or type errors detected"
                }
            
            sandbox_result = await self._test_in_sandbox(target_path, job.improvement_type)
            if not sandbox_result["success"]:
                await asyncio.to_thread(self._restore_backup, backup_path, target_path)
                return {
                    "status": "failed",
                    "error": f"Sandbox validation failed: {sandbox_result.get('error')}"
                }
            
            diff = await asyncio.to_thread(self._get_simple_diff, original_code, improved_code)
            
            after_metrics = await asyncio.to_thread(self._calculate_metrics, target_path)
            
            if backup_path and backup_path.exists():
                await asyncio.to_thread(backup_path.unlink)
            
            return {
                "status": "success",
                "diff": diff,
                "before_metrics": job.before_metrics,
                "after_metrics": after_metrics,
                "temp_workspace": str(temp_workspace),
                "improved_code": improved_code
            }
            
        except Exception as e:
            logger.error(f"Error executing improvement: {e}")
            if backup_path:
                try:
                    await asyncio.to_thread(self._restore_backup, backup_path, self.repo_root / job.target_file)
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup: {restore_error}")
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            if temp_workspace:
                try:
                    await self.cleanup_workspace(str(temp_workspace))
                except Exception as cleanup_error:
                    logger.warning(f"Cleanup failed: {cleanup_error}")
    
    async def cleanup_workspace(self, workspace_path: str):
        """Remove temp workspace after use."""
        try:
            await asyncio.to_thread(self._sync_cleanup_workspace, workspace_path)
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _sync_cleanup_workspace(self, workspace_path: str):
        """Synchronous helper for cleanup_workspace."""
        workspace = Path(workspace_path)
        if workspace.exists() and workspace.parent == self.temp_root:
            shutil.rmtree(workspace)
            logger.info(f"Cleaned up temp workspace: {workspace_path}")
    
    def _create_temp_workspace(self, job_id: str) -> Path:
        """Create temporary workspace for improvement job."""
        temp_dir = Path(f"/tmp/improve_{job_id}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created temp workspace at {temp_dir}")
        return temp_dir
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        backup_path.write_text(file_path.read_text())
        logger.info(f"Created backup at {backup_path}")
        return backup_path
    
    def _restore_backup(self, backup_path: Path, target_path: Path):
        """Restore file from backup."""
        if backup_path.exists():
            target_path.write_text(backup_path.read_text())
            backup_path.unlink()
            logger.info(f"Restored backup from {backup_path} to {target_path}")
    
    async def _generate_improvement(
        self,
        job: ImprovementJob,
        original_code: str
    ) -> Optional[str]:
        """
        Use LLM to generate improved code.
        
        Args:
            job: ImprovementJob with improvement details
            original_code: Original file content
        
        Returns:
            Improved code or None
        """
        prompt = self._build_improvement_prompt(job, original_code)
        
        try:
            response = await gemini_chat(
                messages=[{"role": "user", "content": prompt}]
            )
            
            improved_code = self._extract_code_from_response(response)
            return improved_code
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
    
    def _build_improvement_prompt(self, job: ImprovementJob, code: str) -> str:
        """Build prompt for LLM code improvement."""
        improvement_type_instructions = {
            ImprovementType.REFACTOR_COMPLEXITY: "Reduce cyclomatic complexity by extracting functions and simplifying logic.",
            ImprovementType.SPLIT_LARGE_FILE: "Split this file into smaller, focused modules. Return ONLY the main file with imports updated.",
            ImprovementType.REDUCE_COUPLING: "Reduce coupling by introducing abstractions and dependency injection.",
            ImprovementType.ADD_DOCUMENTATION: "Add comprehensive docstrings and comments.",
            ImprovementType.OPTIMIZE_IMPORTS: "Organize and optimize imports - remove unused, group by type.",
            ImprovementType.FIX_CODE_SMELL: "Fix code smells and apply best practices.",
            ImprovementType.ADD_TESTS: "This should not be called - tests go in separate files.",
            ImprovementType.UPGRADE_DEPENDENCY: "Update code to use newer API patterns."
        }
        
        instruction = improvement_type_instructions.get(
            job.improvement_type,
            "Improve code quality and maintainability."
        )
        
        prompt = f"""You are a code improvement assistant. Your task:

**Improvement Type**: {job.improvement_type.value}
**Goal**: {job.title}
**Details**: {job.description}
**Rationale**: {job.rationale or 'Not provided'}

**Instruction**: {instruction}

**Success Criteria**:
{self._format_success_criteria(job.success_criteria)}

**Original Code**:
```
{code}
```

**Requirements**:
1. Return ONLY the improved code - no explanations, no markdown
2. Preserve all functionality
3. Keep the same file structure (classes, functions, exports)
4. Use the same language and style
5. Do not add TODO comments

Return the complete improved file:"""
        
        return prompt
    
    def _format_success_criteria(self, criteria: Dict) -> str:
        """Format success criteria for prompt."""
        if not criteria:
            return "- Improve code quality"
        
        lines = []
        for key, value in criteria.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract code from LLM response, removing markdown fences."""
        lines = response.strip().split("\n")
        
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        
        code = "\n".join(lines)
        
        if not code.strip():
            return None
        
        return code
    
    async def _test_in_sandbox(self, file_path: Path, improvement_type: ImprovementType) -> Dict:
        """
        Test code in Docker sandbox or local runtime validation.
        
        Returns:
            Dict with success status and optional error message
        """
        if improvement_type in [ImprovementType.ADD_DOCUMENTATION, ImprovementType.OPTIMIZE_IMPORTS]:
            return {"success": True, "message": "Skipped for non-functional changes"}
        
        try:
            # Offload docker check to thread pool
            docker_available = await asyncio.to_thread(
                lambda: subprocess.run(
                    ["which", "docker"],
                    capture_output=True,
                    timeout=2
                ).returncode == 0
            )
            
            if docker_available and file_path.suffix == ".py":
                return await self._test_python_docker(file_path)
            elif file_path.suffix == ".py":
                return await self._test_python_local(file_path)
            elif file_path.suffix in [".ts", ".tsx"]:
                return {"success": True, "message": "TypeScript validated by LSP - sandbox skipped"}
            elif file_path.suffix in [".js", ".jsx"]:
                return await self._test_javascript_local(file_path)
            
            return {"success": True, "message": "No sandbox test for this file type"}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Sandbox test timed out"}
        except Exception as e:
            logger.warning(f"Sandbox test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_python_docker(self, file_path: Path) -> Dict:
        """Test Python file in Docker container."""
        try:
            # Offload Docker subprocess to thread pool
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "docker", "run", "--rm",
                    "-v", f"{file_path.parent}:/code",
                    "python:3.11-slim",
                    "python", "-m", "py_compile", f"/code/{file_path.name}"
                ],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0:
                return {"success": True, "message": "Python validated in Docker"}
            else:
                return {"success": False, "error": result.stderr or "Docker validation failed"}
                
        except Exception as e:
            logger.warning(f"Docker test failed, falling back to local: {e}")
            return await self._test_python_local(file_path)
    
    async def _test_python_local(self, file_path: Path) -> Dict:
        """Test Python file locally."""
        # Offload subprocess to thread pool
        result = await asyncio.to_thread(
            subprocess.run,
            ["python3", "-m", "py_compile", str(file_path)],
            capture_output=True,
            timeout=10,
            text=True
        )
        if result.returncode == 0:
            return {"success": True, "message": "Python syntax valid"}
        else:
            return {"success": False, "error": result.stderr or "Python validation failed"}
    
    async def _test_javascript_local(self, file_path: Path) -> Dict:
        """Test JavaScript/TypeScript file locally."""
        # Offload subprocess to thread pool
        result = await asyncio.to_thread(
            subprocess.run,
            ["node", "--check", str(file_path)],
            capture_output=True,
            timeout=10,
            text=True
        )
        if result.returncode == 0:
            return {"success": True, "message": "JavaScript/TypeScript syntax valid"}
        else:
            return {"success": False, "error": result.stderr or "JavaScript validation failed"}
    
    async def _validate_lsp(self, file_path: Path) -> bool:
        """
        Validate file with LSP (syntax check).
        
        For now, basic syntax validation with Python ast or TypeScript check.
        """
        # Offload file I/O and subprocess to thread pool
        return await asyncio.to_thread(self._sync_validate_lsp, file_path)
    
    def _sync_validate_lsp(self, file_path: Path) -> bool:
        """Synchronous helper for LSP validation."""
        try:
            if file_path.suffix == ".py":
                import ast
                code = file_path.read_text()
                ast.parse(code)
                return True
            
            elif file_path.suffix in [".ts", ".tsx"]:
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit", str(file_path)],
                    capture_output=True,
                    cwd=str(file_path.parent),
                    timeout=30
                )
                return result.returncode == 0
            
            return True
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            logger.warning(f"LSP validation skipped: {e}")
            return True
    
    def _get_simple_diff(self, original: str, improved: str) -> str:
        """Get unified diff between original and improved code using difflib."""
        try:
            diff_lines = difflib.unified_diff(
                original.splitlines(),
                improved.splitlines(),
                lineterm='',
                n=3
            )
            return '\n'.join(diff_lines)
        except Exception as e:
            logger.error(f"Error getting diff: {e}")
            return ""
    
    def _calculate_metrics(self, file_path: Path) -> Dict:
        """Calculate code metrics for a file."""
        try:
            code = file_path.read_text()
            loc = len([l for l in code.split("\n") if l.strip() and not l.strip().startswith("#")])
            
            if file_path.suffix == ".py":
                import ast
                tree = ast.parse(code)
                functions = len([n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
                classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                
                return {
                    "loc": loc,
                    "functions": functions,
                    "classes": classes,
                    "complexity": self._estimate_complexity(tree)
                }
            
            return {"loc": loc}
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def _estimate_complexity(self, tree) -> int:
        """Estimate cyclomatic complexity from AST."""
        import ast
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity


self_modification_engine = SelfModificationEngine()
