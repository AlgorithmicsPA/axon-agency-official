"""LLM Router Service - Multi-LLM orchestration with fallback chain and auto-classification."""

import asyncio
import httpx
import logging
import re
import time
from typing import Optional, Any
from collections import defaultdict

from app.core.config import settings
from app.models.llm import TaskType, LLMResponse, ProviderStatus
from app.providers.openai import openai_chat
from app.providers.gemini import gemini_chat
from app.providers.ollama import ollama_chat

logger = logging.getLogger(__name__)


class LLMRouterService:
    """Intelligent LLM router with fallback chain and automatic task classification."""
    
    def __init__(self):
        """Initialize the LLM router service."""
        self._metrics = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_latency_ms": 0.0,
            "avg_latency_ms": 0.0,
            "success_rate": 0.0
        })
        self._initialized = False
        
    async def initialize(self):
        """Initialize the router and detect available providers."""
        if self._initialized:
            return
            
        logger.info("Initializing LLM Router Service...")
        
        # Auto-detect Ollama availability
        settings.ollama_available = await self._check_ollama_available()
        
        if settings.ollama_available:
            logger.info("✅ Ollama detected and available")
        else:
            logger.info("❌ Ollama not available")
            
        # Log available providers
        available_providers = []
        if settings.ollama_available:
            available_providers.append("Ollama (local)")
        if settings.gemini_api_key:
            available_providers.append("Gemini")
        if settings.openai_api_key:
            available_providers.append("OpenAI")
            
        logger.info(f"Available LLM providers: {', '.join(available_providers)}")
        
        self._initialized = True
        
    async def _check_ollama_available(self) -> bool:
        """Check if Ollama is running on port 11434."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.ollama_base_url}/api/tags",
                    timeout=2.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def _classify_task(self, prompt: str, context: Optional[dict] = None) -> TaskType:
        """Automatically classify the task type based on prompt and context.
        
        Args:
            prompt: The user prompt
            context: Optional context with hints like 'has_images', 'language', etc.
            
        Returns:
            TaskType enum value
        """
        prompt_lower = prompt.lower()
        
        # Check context hints first
        if context:
            if context.get("has_images") or context.get("images"):
                return TaskType.MULTIMODAL
            if context.get("task_type"):
                # Allow explicit override
                try:
                    return TaskType(context["task_type"])
                except ValueError:
                    pass
        
        # Multimodal detection
        if any(word in prompt_lower for word in ["image", "picture", "photo", "visual", "analyze this"]):
            return TaskType.MULTIMODAL
        
        # Code generation detection
        code_keywords = [
            "code", "function", "class", "implement", "write a", "create a script",
            "debug", "refactor", "python", "javascript", "typescript", "java",
            "api", "endpoint", "sql", "query", "algorithm", "program"
        ]
        if any(keyword in prompt_lower for keyword in code_keywords):
            return TaskType.CODE_GENERATION
        
        # Complex reasoning detection
        complex_keywords = [
            "analyze", "compare", "evaluate", "reasoning", "logic", "prove",
            "explain why", "detailed analysis", "comprehensive", "strategic",
            "architecture", "design pattern", "best practices", "trade-offs"
        ]
        if any(keyword in prompt_lower for keyword in complex_keywords):
            if len(prompt) > 200:  # Long complex prompts
                return TaskType.COMPLEX_REASONING
        
        # Image generation detection
        if any(word in prompt_lower for word in ["generate image", "create image", "draw", "render"]):
            return TaskType.IMAGE_GENERATION
        
        # Default to simple text for short, straightforward queries
        return TaskType.SIMPLE_TEXT
    
    async def _execute_with_provider(
        self,
        provider: str,
        prompt: str,
        context: Optional[dict] = None,
        max_retries: int = 3
    ) -> tuple[str, int, float]:
        """Execute LLM call with a specific provider with retry logic.
        
        Args:
            provider: Provider name ("ollama", "gemini", "openai")
            prompt: The prompt to execute
            context: Optional context (images, model preferences, etc.)
            max_retries: Maximum retry attempts with exponential backoff
            
        Returns:
            Tuple of (content, tokens_used, latency_ms)
            
        Raises:
            Exception if all retries fail
        """
        messages = [{"role": "user", "content": prompt}]
        images = context.get("images") if context else None
        model = context.get("model") if context else None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                if provider == "ollama":
                    if not settings.ollama_available:
                        raise ValueError("Ollama not available")
                    content = await ollama_chat(messages, model=model)
                    
                elif provider == "gemini":
                    if not settings.gemini_api_key:
                        raise ValueError("Gemini API key not configured")
                    content = await gemini_chat(messages, model=model, images=images)
                    
                elif provider == "openai":
                    if not settings.openai_api_key:
                        raise ValueError("OpenAI API key not configured")
                    content = await openai_chat(messages, model=model)
                    
                else:
                    raise ValueError(f"Unknown provider: {provider}")
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Estimate tokens (rough approximation)
                tokens_used = len(content.split()) + len(prompt.split())
                
                return content, tokens_used, latency_ms
                
            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Provider {provider} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Provider {provider} failed after {max_retries} attempts: {e}")
                    raise
        
        # This should never be reached due to the raise above, but satisfies type checker
        raise Exception(f"Provider {provider} failed to execute")
    
    async def _execute_with_fallback(
        self,
        task_type: TaskType,
        prompt: str,
        context: Optional[dict] = None
    ) -> LLMResponse:
        """Execute LLM call with fallback chain based on task type.
        
        Args:
            task_type: Type of task to execute
            prompt: The prompt to execute
            context: Optional context
            
        Returns:
            LLMResponse with result and metadata
        """
        # Get provider preference list for this task type
        task_type_map = {
            TaskType.SIMPLE_TEXT: "simple",
            TaskType.CODE_GENERATION: "code",
            TaskType.MULTIMODAL: "multimodal",
            TaskType.COMPLEX_REASONING: "complex",
            TaskType.IMAGE_GENERATION: "image"
        }
        
        preference_key = task_type_map.get(task_type, "simple")
        provider_chain = settings.llm_preferences.get(preference_key, ["gemini", "openai"])
        
        # Filter to only available providers
        available_chain = []
        for provider in provider_chain:
            if provider == "ollama" and settings.ollama_available:
                available_chain.append(provider)
            elif provider == "gemini" and settings.gemini_api_key:
                available_chain.append(provider)
            elif provider == "openai" and settings.openai_api_key:
                available_chain.append(provider)
            elif provider == "sdxl":
                # TODO: Implement SDXL for image generation
                logger.debug("SDXL not yet implemented")
        
        if not available_chain:
            raise ValueError("No LLM providers available for this task")
        
        logger.info(f"Task type: {task_type.value}, Provider chain: {available_chain}")
        
        # Try each provider in the chain
        last_exception = None
        fallback_used = False
        
        for idx, provider in enumerate(available_chain):
            if idx > 0:
                fallback_used = True
                logger.info(f"Falling back to provider: {provider}")
            
            try:
                self._metrics[provider]["total_requests"] += 1
                
                content, tokens_used, latency_ms = await self._execute_with_provider(
                    provider, prompt, context
                )
                
                # Update success metrics
                self._metrics[provider]["successful_requests"] += 1
                self._metrics[provider]["total_tokens"] += tokens_used
                self._metrics[provider]["total_latency_ms"] += latency_ms
                self._update_derived_metrics(provider)
                
                logger.info(
                    f"✅ Success with {provider} - {latency_ms:.0f}ms, "
                    f"{tokens_used} tokens, fallback: {fallback_used}"
                )
                
                return LLMResponse(
                    provider=provider,
                    content=content,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    fallback_used=fallback_used,
                    task_type=task_type,
                    model_used=context.get("model") if context else None
                )
                
            except Exception as e:
                self._metrics[provider]["failed_requests"] += 1
                self._update_derived_metrics(provider)
                last_exception = e
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        # All providers failed
        raise Exception(
            f"All providers in chain failed for task {task_type.value}. "
            f"Last error: {last_exception}"
        )
    
    def _update_derived_metrics(self, provider: str):
        """Update calculated metrics like averages and success rate."""
        metrics = self._metrics[provider]
        
        # Calculate average latency
        if metrics["successful_requests"] > 0:
            metrics["avg_latency_ms"] = (
                metrics["total_latency_ms"] / metrics["successful_requests"]
            )
        
        # Calculate success rate
        if metrics["total_requests"] > 0:
            metrics["success_rate"] = (
                metrics["successful_requests"] / metrics["total_requests"]
            )
    
    async def route_and_execute(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        context: Optional[dict] = None
    ) -> LLMResponse:
        """Route and execute an LLM request with automatic classification and fallback.
        
        This is the main entry point for the LLM router.
        
        Args:
            prompt: The user prompt
            task_type: Optional explicit task type (auto-detected if None)
            context: Optional context with images, model preferences, etc.
            
        Returns:
            LLMResponse with the result and metadata
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Classify task if not provided
        if task_type is None:
            task_type = self._classify_task(prompt, context)
            logger.info(f"Auto-classified task as: {task_type.value}")
        
        # Execute with fallback chain
        return await self._execute_with_fallback(task_type, prompt, context)
    
    def get_metrics(self) -> dict[str, dict]:
        """Get aggregated metrics for all providers.
        
        Returns:
            Dict mapping provider names to their metrics
        """
        return dict(self._metrics)
    
    async def get_provider_status(self) -> list[ProviderStatus]:
        """Get current status and health of all providers.
        
        Returns:
            List of ProviderStatus objects
        """
        statuses = []
        
        # Check Ollama
        ollama_available = await self._check_ollama_available()
        ollama_metrics = self._metrics.get("ollama", {})
        statuses.append(ProviderStatus(
            provider="ollama",
            available=ollama_available,
            latency_avg=ollama_metrics.get("avg_latency_ms", 0.0),
            success_rate=ollama_metrics.get("success_rate", 0.0),
            total_requests=int(ollama_metrics.get("total_requests", 0)),
            successful_requests=int(ollama_metrics.get("successful_requests", 0)),
            failed_requests=int(ollama_metrics.get("failed_requests", 0))
        ))
        
        # Check Gemini
        gemini_metrics = self._metrics.get("gemini", {})
        statuses.append(ProviderStatus(
            provider="gemini",
            available=bool(settings.gemini_api_key),
            latency_avg=gemini_metrics.get("avg_latency_ms", 0.0),
            success_rate=gemini_metrics.get("success_rate", 0.0),
            total_requests=int(gemini_metrics.get("total_requests", 0)),
            successful_requests=int(gemini_metrics.get("successful_requests", 0)),
            failed_requests=int(gemini_metrics.get("failed_requests", 0))
        ))
        
        # Check OpenAI
        openai_metrics = self._metrics.get("openai", {})
        statuses.append(ProviderStatus(
            provider="openai",
            available=bool(settings.openai_api_key),
            latency_avg=openai_metrics.get("avg_latency_ms", 0.0),
            success_rate=openai_metrics.get("success_rate", 0.0),
            total_requests=int(openai_metrics.get("total_requests", 0)),
            successful_requests=int(openai_metrics.get("successful_requests", 0)),
            failed_requests=int(openai_metrics.get("failed_requests", 0))
        ))
        
        return statuses


# Global singleton instance
_router_service: Optional[LLMRouterService] = None


def get_llm_router() -> LLMRouterService:
    """Get or create the global LLM router instance."""
    global _router_service
    if _router_service is None:
        _router_service = LLMRouterService()
    return _router_service
