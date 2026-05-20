"""Proveedor LLM para OpenRouter."""
from typing import Any

import requests

from src.config import get_config
from .base import ChatResponse, LLMProvider


class OpenRouterProvider(LLMProvider):
    """Proveedor para OpenRouter (multi-proveedor cloud)."""
    
    name = "openrouter"
    
    def __init__(self, model: str | None = None, api_key: str | None = None):
        config = get_config()
        cfg = config.get_provider("openrouter")
        
        self.model = model or cfg.model if cfg else "anthropic/claude-3-haiku-20240307"
        self.api_key = api_key or cfg.api_key or ""
        self.base_url = cfg.base_url if cfg else "https://openrouter.ai/api/v1"
        self.timeout = cfg.timeout if cfg else 60
    
    def _get_headers(self) -> dict:
        """Headers para requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hermes-agent",
            "X-Title": "Hermes Agent",
        }
    
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Envía mensajes a OpenRouter."""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
        }
        
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        if "system" in kwargs:
            payload["messages"] = [{"role": "system", "content": kwargs["system"]}] + messages
        
        response = requests.post(
            url,
            json=payload,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Completa un prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def get_available_models(self) -> list[str]:
        """Lista modelos disponibles."""
        try:
            response = requests.get(
                "https://openrouter.ai/models",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return [m.get("id", "") for m in data.get("data", [])]
        except Exception:
            return []
    
    def is_available(self) -> bool:
        """Verifica si hay conexión."""
        return bool(self.api_key)