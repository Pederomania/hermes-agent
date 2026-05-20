"""Proveedor LLM para OpenAI."""
import os
from typing import Any

import requests

from src.config import get_config
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Proveedor para OpenAI."""
    
    name = "openai"
    
    def __init__(self, model: str | None = None, api_key: str | None = None):
        config = get_config()
        cfg = config.get_provider("openai")
        
        self.model = model or cfg.model if cfg else "gpt-4-turbo-preview"
        self.api_key = api_key or cfg.api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = cfg.base_url if cfg else "https://api.openai.com/v1"
        self.timeout = cfg.timeout if cfg else 60
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
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
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def get_available_models(self) -> list[str]:
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return [m.get("id", "") for m in data.get("data", [])]
        except Exception:
            return []
    
    def is_available(self) -> bool:
        return bool(self.api_key)