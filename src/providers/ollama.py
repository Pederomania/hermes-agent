"""Proveedor LLM para Ollama (local)."""
import json
from typing import Any

import requests

from src.config import get_config
from .base import ChatResponse, LLMProvider


class OllamaProvider(LLMProvider):
    """Proveedor para Ollama (endpoint local)."""
    
    name = "ollama"
    
    def __init__(self, model: str | None = None, endpoint: str | None = None):
        config = get_config()
        cfg = config.get_provider("ollama")
        
        self.model = model or cfg.model if cfg else "llama3"
        self.endpoint = endpoint or cfg.endpoint if cfg else "http://localhost:11434"
        self.timeout = cfg.timeout if cfg else 120
    
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Envía mensajes a Ollama."""
        url = f"{self.endpoint}/api/chat"
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 4096),
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        return data.get("message", {}).get("content", "")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Completa un prompt simple."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def get_available_models(self) -> list[str]:
        """Lista modelos disponibles en Ollama."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []
    
    def is_available(self) -> bool:
        """Verifica si Ollama está disponible."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False