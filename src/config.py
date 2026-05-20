"""Sistema de configuración multi-proveedor."""
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Configuración de un proveedor LLM."""
    enabled: bool = False
    endpoint: str = ""
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: int = 60


class AgentConfig(BaseModel):
    """Configuración del agente."""
    max_context_tokens: int = 4096
    summarize_after: int = 3000
    temperature: float = 0.7
    history_file: str = "memory/history.db"


class Config(BaseModel):
    """Configuración principal."""
    providers: dict[str, ProviderConfig] = {}
    default_provider: str = "ollama"
    agent: AgentConfig = Field(default_factory=AgentConfig)

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "Config":
        """Carga la configuración desde el archivo YAML."""
        if config_path is None:
            # Default to config/models.yaml in project root
            config_path = Path.cwd() / "config" / "models.yaml"
        
        config_path = Path(config_path)
        if not config_path.exists():
            return cls()
        
        with open(config_path) as f:
            data = yaml.safe_load(f)
        
        # Procesar variables de entorno en api_key
        providers = {}
        for name, pdata in data.get("providers", {}).items():
            api_key = pdata.get("api_key", "")
            if api_key.startswith("${") and api_key.endswith("}"):
                env_var = api_key[2:-1]
                api_key = os.getenv(env_var, "")
            pdata["api_key"] = api_key
            providers[name] = ProviderConfig(**pdata)
        
        return cls(
            providers=providers,
            default_provider=data.get("default_provider", "ollama"),
            agent=AgentConfig(**data.get("agent", {}))
        )

    def get_provider(self, name: str | None = None) -> ProviderConfig | None:
        """Obtiene la configuración de un proveedor."""
        if name is None:
            name = self.default_provider
        return self.providers.get(name)

    def list_enabled_providers(self) -> list[str]:
        """Lista proveedores habilitados."""
        return [name for name, p in self.providers.items() if p.enabled]


# Instancia global de configuración
_config: Config | None = None


def get_config() -> Config:
    """Obtiene la configuración global."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """Recarga la configuración."""
    global _config
    _config = Config.load()
    return _config