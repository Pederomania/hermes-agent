"""Registry de herramientas del agente."""
from typing import Type

from .base import Tool
from .code import CodeTool, get_code_tool
from .file import FileTool, get_file_tool
from .shell import ShellTool, get_shell_tool
from .web import WebSearchTool, get_web_search_tool


# Registry de herramientas
TOOLS: dict[str, Type[Tool]] = {
    "shell": ShellTool,
    "web_search": WebSearchTool,
    "code": CodeTool,
    "file": FileTool,
}


class ToolRegistry:
    """Registry de herramientas disponibles."""
    
    _instances: dict[str, Tool] = {}
    
    @classmethod
    def get(cls, name: str, **kwargs) -> Tool:
        """Obtiene una herramienta."""
        if name not in cls._instances:
            tool_class = TOOLS.get(name)
            if tool_class is None:
                raise ValueError(f"Herramienta desconocida: {name}")
            cls._instances[name] = tool_class(**kwargs)
        
        return cls._instances[name]
    
    @classmethod
    def list_tools(cls) -> list[dict]:
        """Lista todas las herramientas."""
        return [
            {"name": name, "description": tool_class.description}
            for name, tool_class in TOOLS.items()
        ]
    
    @classmethod
    def get_schemas(cls) -> list[dict]:
        """Obtiene schemas JSON."""
        return [cls.get(name).get_schema() for name in TOOLS]
    
    @classmethod
    def clear(cls) -> None:
        """Limpia instancias."""
        cls._instances.clear()


def get_tool(name: str, **kwargs) -> Tool:
    """Helper para obtener herramientas."""
    return ToolRegistry.get(name, **kwargs)


def list_all_tools() -> list[dict]:
    """Lista todas las herramientas."""
    return ToolRegistry.list_tools()


def get_all_schemas() -> list[dict]:
    """Obtiene todos los schemas."""
    return ToolRegistry.get_schemas()