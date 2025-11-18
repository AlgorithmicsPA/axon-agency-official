from typing import Dict, Type, Any, Optional
from loguru import logger


class AdapterRegistry:
    """Registry for adapters (services, LLMs, tunnels, etc.)."""
    
    def __init__(self):
        self._services: Dict[str, Type] = {}
        self._llms: Dict[str, Type] = {}
        self._tunnels: Dict[str, Type] = {}
        self._flows: Dict[str, Type] = {}
    
    def register_service(self, name: str, adapter_class: Type):
        """Register a service adapter."""
        self._services[name] = adapter_class
        logger.debug(f"Registered service adapter: {name}")
    
    def register_llm(self, name: str, adapter_class: Type):
        """Register an LLM adapter."""
        self._llms[name] = adapter_class
        logger.debug(f"Registered LLM adapter: {name}")
    
    def register_tunnel(self, name: str, adapter_class: Type):
        """Register a tunnel adapter."""
        self._tunnels[name] = adapter_class
        logger.debug(f"Registered tunnel adapter: {name}")
    
    def register_flow(self, name: str, adapter_class: Type):
        """Register a flow adapter."""
        self._flows[name] = adapter_class
        logger.debug(f"Registered flow adapter: {name}")
    
    def get_service(self, name: str) -> Optional[Type]:
        """Get service adapter by name."""
        return self._services.get(name)
    
    def get_llm(self, name: str) -> Optional[Type]:
        """Get LLM adapter by name."""
        return self._llms.get(name)
    
    def get_tunnel(self, name: str) -> Optional[Type]:
        """Get tunnel adapter by name."""
        return self._tunnels.get(name)
    
    def get_flow(self, name: str) -> Optional[Type]:
        """Get flow adapter by name."""
        return self._flows.get(name)
    
    def list_services(self) -> list[str]:
        """List registered service adapters."""
        return list(self._services.keys())
    
    def list_llms(self) -> list[str]:
        """List registered LLM adapters."""
        return list(self._llms.keys())
    
    def list_tunnels(self) -> list[str]:
        """List registered tunnel adapters."""
        return list(self._tunnels.keys())
    
    def list_flows(self) -> list[str]:
        """List registered flow adapters."""
        return list(self._flows.keys())


registry = AdapterRegistry()
