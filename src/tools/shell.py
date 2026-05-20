"""Herramienta de shell para ejecutar comandos."""
import re
import subprocess
from typing import Any

from .base import Tool, ToolResult


# Patrones bloqueados por seguridad
BLOCKED_PATTERNS = [
    r'\brm\s+-rf\b',
    r'\bmkfs\b',
    r'\bdd\b.*of=',
    r'\bchmod\s+777\b',
    r'>\s*/dev/',
    r'\bcurl\b.*\|\s*bash',
    r'\bwget\b.*\|\s*sh',
    r':\(\)\{',
    r'\bsudo\s+su\b',
]


class ShellTool(Tool):
    """Ejecuta comandos de shell."""
    
    name = "shell"
    description = "Ejecuta comandos de shell en el sistema operativo"
    
    def __init__(self, working_dir: str | None = None):
        self.working_dir = working_dir
    
    def _is_safe(self, command: str) -> tuple[bool, str]:
        """Valida que el comando sea seguro."""
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Comando bloqueado: {pattern}"
        return True, ""
    
    def execute(self, command: str, timeout: int = 60, **kwargs) -> str:
        """Ejecuta un comando de shell."""
        # Validar seguridad
        safe, reason = self._is_safe(command)
        if not safe:
            return f"❌ {reason}"
        
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
            return f"❌ Timeout despues de {timeout}s"
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