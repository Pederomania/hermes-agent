"""Clase base para herramientas del agente."""
from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Clase base para herramientas."""
    
    name: str = "base"
    description: str = "Descripción de la herramienta"
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Ejecuta la herramienta.
        
        Args:
            **kwargs: Parámetros específicos de cada herramienta.
        
        Returns:
            Resultado como string.
        """
        pass
    
    def get_schema(self) -> dict:
        """Retorna el schema JSON para tool calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> dict:
        """Retorna el schema de parámetros."""
        pass


class ToolResult:
    """Resultado de una herramienta."""
    
    def __init__(
        self,
        output: str,
        success: bool = True,
        error: str | None = None,
        metadata: dict | None = None
    ):
        self.output = output
        self.success = success
        self.error = error
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        return self.output
    
    def __repr__(self) -> str:
        status = "✅" if self.success else "❌"
        return f"{status} {self.output}"