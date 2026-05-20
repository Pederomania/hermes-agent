"""Interfaz abstracta para proveedores LLM."""
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Interfaz abstracta para proveedores LLM."""
    
    name: str = "base"
    
    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """
        Envía mensajes al LLM y retorna la respuesta.
        
        Args:
            messages: Lista de mensajes con formato [{"role": "user|assistant|system", "content": "..."}]
            **kwargs: Parámetros adicionales (temperature, max_tokens, etc.)
        
        Returns:
            Respuesta del LLM como string.
        """
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Completa un prompt simple.
        
        Args:
            prompt: Prompt a completar.
            **kwargs: Parámetros adicionales.
        
        Returns:
            Texto completado.
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos disponibles."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el proveedor está disponible."""
        pass
    
    def format_messages(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Formatea mensajes para el proveedor específico."""
        return messages


class ToolCallResult:
    """Resultado de una llamada a herramienta."""
    
    def __init__(self, tool_name: str, input_data: dict, output: str):
        self.tool_name = tool_name
        self.input_data = input_data
        self.output = output
        self.is_error = False
    
    def __str__(self) -> str:
        return self.output


class ChatResponse:
    """Respuesta de chat con soporte para tool calls."""
    
    def __init__(
        self,
        content: str,
        model: str | None = None,
        tool_calls: list[dict] | None = None,
        usage: dict | None = None
    ):
        self.content = content
        self.model = model
        self.tool_calls = tool_calls or []
        self.usage = usage or {}
    
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0