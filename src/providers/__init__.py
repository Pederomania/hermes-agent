"""Factory para instanciar proveedores LLM."""
from typing import Type

from src.config import get_config
from .base import LLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider


# Registry de proveedores
PROVIDERS: dict[str, Type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
}


class ProviderFactory:
    """Factory para crear proveedores LLM."""
    
    @staticmethod
    def create(provider_name: str | None = None, **kwargs) -> LLMProvider:
        """
        Crea un proveedor LLM.
        
        Args:
            provider_name: Nombre del proveedor. Si es None, usa el provider por defecto.
            **kwargs: Parámetros adicionales para el proveedor.
        
        Returns:
            Instancia del proveedor.
        
        Raises:
            ValueError: Si el proveedor no existe o no está habilitado.
        """
        config = get_config()
        
        if provider_name is None:
            provider_name = config.default_provider
        
        provider_class = PROVIDERS.get(provider_name)
        if provider_class is None:
            raise ValueError(f"Proveedor desconocido: {provider_name}")
        
        cfg = config.get_provider(provider_name)
        if cfg and not cfg.enabled:
            raise ValueError(f"Proveedor no habilitado: {provider_name}")
        
        return provider_class(**kwargs)
    
    @staticmethod
    def list_providers() -> list[str]:
        """Lista proveedores disponibles."""
        config = get_config()
        return config.list_enabled_providers()
    
    @staticmethod
    def get_default() -> LLMProvider:
        """Crea el proveedor por defecto."""
        config = get_config()
        return ProviderFactory.create(config.default_provider)


# Instancia global
_default_provider: LLMProvider | None = None
_provider_name: str | None = None


def get_provider(provider_name: str | None = None, force_new: bool = False) -> LLMProvider:
    """Obtiene un proveedor (helper)."""
    return ProviderFactory.create(provider_name)


def get_default_provider(force_new: bool = False) -> LLMProvider:
    """Obtiene el proveedor por defecto, con opción de forzar nueva instancia."""
    global _default_provider, _provider_name
    config = get_config()
    
    if force_new or _default_provider is None or _provider_name != config.default_provider:
        _default_provider = ProviderFactory.get_default()
        _provider_name = config.default_provider
    
    return _default_provider


def set_default_provider(provider: LLMProvider, provider_name: str | None = None) -> None:
    """Establece el proveedor por defecto."""
    global _default_provider, _provider_name
    _default_provider = provider
    _provider_name = provider_name or type(provider).__name__.lower().replace("provider", "")