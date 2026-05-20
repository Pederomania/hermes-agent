"""Herramienta de shell para ejecutar comandos."""
import subprocess
from typing import Any

from .base import Tool, ToolResult


class ShellTool(Tool):
    """Ejecuta comandos de shell."""
    
    name = "shell"
    description = "Ejecuta comandos de shell en el sistema operativo"
    
    def __init__(self, working_dir: str | None = None):
        self.working_dir = working_dir
    
    def execute(self, command: str, timeout: int = 60, **kwargs) -> str:
        """Ejecuta un comando de shell."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir,
                **kwargs
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr] {result.stderr}"
            
            return output or "[Sin output]"
        
        except subprocess.TimeoutExpired:
            return f"❌ Timeout después de {timeout}s"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Comando a ejecutar"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout en segundos (default: 60)",
                    "default": 60
                }
            },
            "required": ["command"]
        }


# Instancia global
_shell_tool: ShellTool | None = None


def get_shell_tool(working_dir: str | None = None) -> ShellTool:
    global _shell_tool
    if _shell_tool is None:
        _shell_tool = ShellTool(working_dir)
    return _shell_tool


def run_command(command: str, timeout: int = 60) -> str:
    """Helper para ejecutar comandos."""
    return get_shell_tool().execute(command, timeout)