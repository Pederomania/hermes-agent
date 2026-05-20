"""Tests para configuración."""
import pytest
from pathlib import Path

from src.config import Config, ProviderConfig, AgentConfig


def test_provider_config_defaults():
    """Testea默认值 de ProviderConfig."""
    cfg = ProviderConfig()
    assert cfg.enabled is False
    assert cfg.endpoint == ""
    assert cfg.api_key == ""


def test_agent_config_defaults():
    """Testea默认值 de AgentConfig."""
    cfg = AgentConfig()
    assert cfg.max_context_tokens == 4096
    assert cfg.summarize_after == 3000
    assert cfg.temperature == 0.7


def test_config_load():
    """Testea carga de configuración."""
    config = Config.load(Path("config/models.yaml"))
    assert config.default_provider == "ollama"
    assert "ollama" in config.providers
    assert "openrouter" in config.providers


def test_list_enabled_providers():
    """Testea listado de proveedores habilitados."""
    config = Config.load(Path("config/models.yaml"))
    enabled = config.list_enabled_providers()
    assert "ollama" in enabled
    assert "openrouter" in enabled


def test_get_provider():
    """Testea obtención de proveedor."""
    config = Config.load(Path("config/models.yaml"))
    provider = config.get_provider("ollama")
    assert provider is not None
    assert provider.model == "llama3"


def test_get_default_provider():
    """Testea proveedor por defecto."""
    config = Config.load(Path("config/models.yaml"))
    provider = config.get_provider()
    assert provider is not None
    assert provider.model == "llama3"