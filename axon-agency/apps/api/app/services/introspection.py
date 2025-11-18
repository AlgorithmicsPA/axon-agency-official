import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class FileMetrics:
    """Metrics for a single file."""
    path: str
    lines_of_code: int
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    complexity_score: int = 0
    dependencies: Set[str] = field(default_factory=set)
    
    
@dataclass
class CodeStructure:
    """Complete codebase structure."""
    files: Dict[str, FileMetrics]
    dependency_graph: Dict[str, Set[str]]
    total_loc: int
    file_count: int
    language_breakdown: Dict[str, int]


class IntrospectionService:
    """Analyzes the agent's own codebase for self-improvement."""
    
    def __init__(self, root_path: str = "../.."):
        """Initialize with root_path relative to apps/api directory."""
        self.root_path = Path(root_path).resolve()
        self.files: Dict[str, FileMetrics] = {}
        
    def scan_repository(self) -> CodeStructure:
        """Scan the entire repository and build structure map."""
        logger.info(f"Scanning repository at {self.root_path}")
        
        python_files = list(self.root_path.rglob("*.py"))
        typescript_files = list(self.root_path.rglob("*.ts")) + list(self.root_path.rglob("*.tsx"))
        
        # Analyze Python files
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            metrics = self._analyze_python_file(file_path)
            if metrics:
                # Use relative path as key
                self.files[metrics.path] = metrics
        
        # Analyze TypeScript files
        for file_path in typescript_files:
            if self._should_skip(file_path):
                continue
            metrics = self._analyze_typescript_file(file_path)
            if metrics:
                # Use relative path as key
                self.files[metrics.path] = metrics
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph()
        
        # Calculate statistics
        total_loc = sum(f.lines_of_code for f in self.files.values())
        lang_breakdown = self._calculate_language_breakdown()
        
        structure = CodeStructure(
            files=self.files,
            dependency_graph=dep_graph,
            total_loc=total_loc,
            file_count=len(self.files),
            language_breakdown=lang_breakdown
        )
        
        logger.info(f"Scanned {structure.file_count} files, {structure.total_loc} LOC")
        return structure
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_dirs = {"node_modules", "__pycache__", ".next", "dist", "build", ".git"}
        return any(skip_dir in file_path.parts for skip_dir in skip_dirs)
    
    def _analyze_python_file(self, file_path: Path) -> Optional[FileMetrics]:
        """Analyze a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = []
            classes = []
            functions = []
            dependencies = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        dependencies.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    # Handle relative imports (from . import foo, from .. import bar)
                    if node.level > 0:
                        # Relative import
                        if node.module:
                            # from ..providers import openai -> "..providers"
                            imports.append(f".{'.' * (node.level - 1)}{node.module}")
                        # Also add aliases as separate imports (for from ..providers import openai)
                        for alias in node.names:
                            if alias.name != '*':
                                # from ..providers import openai -> "..providers.openai"
                                base = f".{'.' * (node.level - 1)}{node.module}" if node.module else f".{'.' * (node.level - 1)}"
                                if node.module:
                                    imports.append(f"{base}.{alias.name}")
                                else:
                                    imports.append(f"{base}{alias.name}")
                    elif node.module:
                        # Absolute import: from app.providers import openai
                        imports.append(node.module)
                        dependencies.add(node.module.split('.')[0])
                        # Also add full module paths for each imported symbol
                        for alias in node.names:
                            if alias.name != '*':
                                imports.append(f"{node.module}.{alias.name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
            
            lines = content.split('\n')
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            # Simple complexity: number of functions + classes + imports
            complexity = len(functions) + len(classes) + len(imports)
            
            # Store with relative path for consistent keys
            rel_path = str(file_path.relative_to(self.root_path))
            
            return FileMetrics(
                path=rel_path,
                lines_of_code=loc,
                imports=imports,
                classes=classes,
                functions=functions,
                complexity_score=complexity,
                dependencies=dependencies
            )
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return None
    
    def _analyze_typescript_file(self, file_path: Path) -> Optional[FileMetrics]:
        """Analyze a TypeScript file (basic regex-based analysis)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith('//'))
            
            # Extract imports (basic)
            imports = []
            dependencies = set()
            for line in lines:
                line = line.strip()
                if line.startswith('import '):
                    imports.append(line)
                    # Extract module name
                    if 'from' in line:
                        module = line.split('from')[-1].strip().strip("';\"")
                        if not module.startswith('.'):
                            dependencies.add(module.split('/')[0])
            
            # Extract functions/components (very basic)
            functions = []
            for line in lines:
                if 'function ' in line or 'const ' in line and '=>' in line:
                    parts = line.split()
                    if 'function' in parts:
                        idx = parts.index('function') + 1
                        if idx < len(parts):
                            functions.append(parts[idx].split('(')[0])
                    elif 'const' in parts:
                        idx = parts.index('const') + 1
                        if idx < len(parts):
                            functions.append(parts[idx].split('=')[0].strip())
            
            complexity = len(functions) + len(imports)
            
            # Store with relative path for consistent keys
            rel_path = str(file_path.relative_to(self.root_path))
            
            return FileMetrics(
                path=rel_path,
                lines_of_code=loc,
                imports=imports,
                classes=[],
                functions=functions,
                complexity_score=complexity,
                dependencies=dependencies
            )
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return None
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build file dependency graph from imports.
        
        Resolves both absolute and relative imports to actual file paths.
        """
        graph = {}
        
        # Build module-to-file mapping for absolute imports
        module_to_file = self._build_module_map()
        
        # Process each file's imports
        for file_path, metrics in self.files.items():
            graph[file_path] = set()
            
            # Resolve each import
            for imp in metrics.imports:
                # Relative import - resolve based on current file's package
                if imp.startswith('.'):
                    target = self._resolve_relative_import(file_path, imp)
                    if target and target in self.files:
                        graph[file_path].add(target)
                # Absolute import - use module map
                else:
                    if imp in module_to_file:
                        graph[file_path].add(module_to_file[imp])
        
        return graph
    
    def _build_module_map(self) -> Dict[str, str]:
        """Build mapping of module names to file paths."""
        module_map = {}
        
        for file_path in self.files.keys():
            if not file_path.endswith('.py'):
                continue
            
            # Convert file path to module name
            # e.g., "apps/api/app/services/introspection.py" -> "app.services.introspection"
            parts = Path(file_path).parts
            
            # Find 'app' directory (or 'apps')
            app_index = None
            for i, part in enumerate(parts):
                if part == 'app' and i > 0:
                    app_index = i
                    break
            
            if app_index is None:
                continue
            
            # Build module name
            module_parts = list(parts[app_index:])
            module_parts[-1] = Path(module_parts[-1]).stem  # Remove .py extension
            
            # Handle __init__.py
            if module_parts[-1] == '__init__':
                module_parts.pop()  # Package import
            
            module_name = '.'.join(module_parts)
            module_map[module_name] = file_path
        
        return module_map
    
    def _resolve_relative_import(self, current_file: str, relative_import: str) -> Optional[str]:
        """Resolve relative import to absolute file path.
        
        Handles both module imports (from ..foo import bar) and package imports (from .. import foo).
        
        Args:
            current_file: Path of file doing the import
            relative_import: Relative import string (e.g., ".vector_store" or "..providers" or "..routers.projects")
        
        Returns:
            Resolved file path or None
        """
        # Count leading dots
        level = 0
        while level < len(relative_import) and relative_import[level] == '.':
            level += 1
        
        # Extract module name after dots
        module_name = relative_import[level:] if level < len(relative_import) else ""
        
        # Get current file's directory parts
        parts = list(Path(current_file).parts)
        parts.pop()  # Remove filename
        
        # Go up 'level-1' directories (level=1 means same directory)
        for _ in range(level - 1):
            if parts:
                parts.pop()
        
        # Add module parts
        if module_name:
            module_parts = module_name.split('.')
            parts.extend(module_parts)
        
        # Try module file first (e.g., "foo/bar.py")
        target_path = '/'.join(parts) + '.py'
        if target_path in self.files:
            return target_path
        
        # Try package init file (e.g., "foo/bar/__init__.py")
        package_path = '/'.join(parts) + '/__init__.py'
        if package_path in self.files:
            return package_path
        
        return None
    
    def _calculate_language_breakdown(self) -> Dict[str, int]:
        """Calculate LOC by language."""
        breakdown = {"Python": 0, "TypeScript": 0}
        
        for file_path, metrics in self.files.items():
            if file_path.endswith('.py'):
                breakdown["Python"] += metrics.lines_of_code
            elif file_path.endswith(('.ts', '.tsx')):
                breakdown["TypeScript"] += metrics.lines_of_code
        
        return breakdown
    
    def find_improvement_opportunities(self, structure: CodeStructure) -> List[Dict[str, Any]]:
        """Identify potential improvement areas."""
        opportunities = []
        
        # Find large files
        for file_path, metrics in structure.files.items():
            if metrics.lines_of_code > 300:
                opportunities.append({
                    "type": "large_file",
                    "severity": "medium",
                    "file": file_path,
                    "message": f"File has {metrics.lines_of_code} LOC - consider splitting",
                    "loc": metrics.lines_of_code
                })
        
        # Find complex files
        for file_path, metrics in structure.files.items():
            if metrics.complexity_score > 50:
                opportunities.append({
                    "type": "high_complexity",
                    "severity": "high",
                    "file": file_path,
                    "message": f"High complexity score ({metrics.complexity_score}) - refactor recommended",
                    "complexity": metrics.complexity_score
                })
        
        # Find files with many dependencies
        for file_path, deps in structure.dependency_graph.items():
            if len(deps) > 8:
                opportunities.append({
                    "type": "high_coupling",
                    "severity": "medium",
                    "file": file_path,
                    "message": f"File depends on {len(deps)} other files - high coupling",
                    "dependency_count": len(deps)
                })
        
        # Find files with no documentation
        for file_path, metrics in structure.files.items():
            if len(metrics.classes) > 0 or len(metrics.functions) > 5:
                opportunities.append({
                    "type": "missing_docs",
                    "severity": "low",
                    "file": file_path,
                    "message": f"File with {len(metrics.functions)} functions may need documentation",
                    "function_count": len(metrics.functions)
                })
        
        # Sort by severity (high first) and then by metric value
        severity_order = {"high": 0, "medium": 1, "low": 2}
        opportunities.sort(key=lambda x: (severity_order[x["severity"]], -x.get("loc", x.get("complexity", x.get("dependency_count", 0)))))
        
        return opportunities[:20]  # Top 20 opportunities
