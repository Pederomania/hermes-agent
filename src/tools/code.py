"""Herramienta de código para análisis y generación."""
import os
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult


class CodeTool(Tool):
    """Herramienta para análisis y generación de código."""
    
    name = "code"
    description = "Analiza, genera y revisa código en múltiples lenguajes"
    
    def __init__(self, workspace: str | Path | None = None, provider=None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.provider = provider
    
    def execute(
        self,
        action: str = "analyze",
        file_path: str | None = None,
        code: str | None = None,
        language: str | None = None,
        **kwargs
    ) -> str:
        """Ejecuta acción de código."""
        actions = {
            "analyze": self._analyze,
            "generate": self._generate,
            "review": self._review,
            "format": self._format,
            "lint": self._lint,
        }
        
        handler = actions.get(action, self._analyze)
        
        if action == "generate":
            return handler(code or "", language or "python", **kwargs)
        elif action == "analyze" and file_path:
            return handler(file_path, **kwargs)
        elif action == "review":
            return handler(code or "", **kwargs)
        else:
            return handler(file_path or "", **kwargs)
    
    def _analyze(self, file_path: str, **kwargs) -> str:
        """Analiza un archivo de código."""
        path = self.workspace / file_path if not Path(file_path).is_absolute() else Path(file_path)
        
        if not path.exists():
            return f"❌ Archivo no encontrado: {file_path}"
        
        try:
            with open(path) as f:
                content = f.read()
            
            lines = content.split("\n")
            extension = path.suffix
            
            return f"📄 {path.name} ({len(lines)} líneas, {extension})"
        
        except Exception as e:
            return f"❌ Error al leer: {str(e)}"
    
    def _generate(self, prompt: str, language: str = "python", **kwargs) -> str:
        """Genera codigo basado en un prompt usando el LLM."""
        if not self.provider:
            return f"# Code {language} based on: {prompt}\n# (No LLM provider configured)"
        
        prompt_text = f"Generate {language} code for the following requirement:\n{prompt}\n\nOnly return the code, no explanation."
        
        try:
            result = self.provider.complete(prompt_text)
            return result
        except Exception as e:
            return f"# Error: {e}"
    
    def _review(self, code: str, **kwargs) -> str:
        """Revisa código."""
        if not code:
            return "❌ No hay código para revisar"
        
        issues = []
        
        # Checks básicos
        if len(code) > 5000:
            issues.append("⚠️ Código muy largo, considera dividirlo")
        
        if "password" in code.lower() and "=" in code:
            issues.append("🔐 Posible contraseña hardcodeada")
        
        if "eval(" in code or "exec(" in code:
            issues.append("⚠️ Uso de eval/exec puede ser peligroso")
        
        if not issues:
            issues.append("✅ No se encontraron issues obvious")
        
        return "\n".join(issues)
    
    def _format(self, file_path: str, **kwargs) -> str:
        """Formatea código."""
        return f"⌨️ Formateando {file_path}..."
    
    def _lint(self, file_path: str, **kwargs) -> str:
        """Lintea código."""
        return f"🔍 Lenteando {file_path}..."
    
    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Acción: analyze, generate, review, format, lint",
                    "enum": ["analyze", "generate", "review", "format", "lint"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Ruta del archivo (para analyze, format, lint)"
                },
                "code": {
                    "type": "string",
                    "description": "Código (para generate, review)"
                },
                "language": {
                    "type": "string",
                    "description": "Lenguaje de programación"
                }
            },
            "required": ["action"]
        }


# Instancia global
_code_tool: CodeTool | None = None


def get_code_tool(workspace: str | Path | None = None) -> CodeTool:
    global _code_tool
    if _code_tool is None:
        _code_tool = CodeTool(workspace)
    return _code_tool