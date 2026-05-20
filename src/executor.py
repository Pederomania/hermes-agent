"""Executor: ejecuta las acciones del planner."""
import json
import subprocess
from typing import Any

from src.tools import get_tool
from src.tools.base import Tool


class Executor:
    """Ejecutor de acciones."""
    
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self._init_tools()
    
    def _init_tools(self) -> None:
        """Inicializa las herramientas disponibles."""
        self.tools = {
            "shell": get_tool("shell"),
            "file": get_tool("file"),
            "code": get_tool("code"),
            "web_search": get_tool("web_search"),
        }
    
    def execute(self, action: str, args: dict) -> str:
        """
        Ejecuta una acción.
        
        Args:
            action: Nombre de la acción a ejecutar
            args: Argumentos para la acción
        
        Returns:
            Resultado de la ejecución
        """
        if action == "echo":
            return args.get("message", "")
        
        # Get tool
        tool = self.tools.get(action)
        if tool is None:
            return f"❌ Herramienta desconocida: {action}"
        
        # Execute
        try:
            result = tool.execute(**args)
            return str(result)
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def execute_ssh(self, host: str, command: str, timeout: int = 60) -> str:
        """Ejecuta comando SSH."""
        from src.tools.shell import ShellTool
        
        shell = ShellTool()
        full_command = f"ssh -o StrictHostKeyChecking=no user@{host} '{command}'"
        
        return shell.execute(full_command, timeout=timeout)
    
    def get_available_tools(self) -> list[str]:
        """Lista herramientas disponibles."""
        return list(self.tools.keys())


# Instancia global
_executor: Executor | None = None


def get_executor() -> Executor:
    """Obtiene el executor."""
    global _executor
    if _executor is None:
        _executor = Executor()
    return _executor