"""Tests para proveedores."""
import pytest

from src.providers import ProviderFactory


def test_provider_factory_ollama():
    """Testea creación de proveedor Ollama."""
    provider = ProviderFactory.create("ollama")
    assert provider.name == "ollama"


def test_provider_factory_list():
    """Testea listado de proveedores."""
    providers = ProviderFactory.list_providers()
    assert "ollama" in providers


def test_provider_factory_unknown():
    """Testea proveedor desconocido."""
    with pytest.raises(ValueError):
        ProviderFactory.create("unknown_provider")


def test_provider_factory_disabled():
    """Testea proveedor deshabilitado."""
    with pytest.raises(ValueError):
        ProviderFactory.create("anthropic")