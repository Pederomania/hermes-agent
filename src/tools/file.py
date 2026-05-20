"""Herramienta de archivos para lectura y escritura."""
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult


class FileTool(Tool):
    """Herramienta para leer y escribir archivos."""
    
    name = "file"
    description = "Lee, escribe y lista archivos"
    
    def __init__(self, workspace: str | Path | None = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
    
    def execute(
        self,
        action: str = "read",
        path: str | None = None,
        content: str | None = None,
        **kwargs
    ) -> str:
        """Ejecuta acción de archivo."""
        actions = {
            "read": self._read,
            "write": self._write,
            "append": self._append,
            "list": self._list,
            "delete": self._delete,
            "exists": self._exists,
        }
        
        handler = actions.get(action, self._read)
        return handler(path or "", content, **kwargs)
    
    def _resolve_path(self, path_str: str) -> Path:
        """Resuelve ruta relativa al workspace."""
        path = Path(path_str)
        if path.is_absolute():
            return path
        return self.workspace / path
    
    def _read(self, path: str, **kwargs) -> str:
        """Lee un archivo."""
        if not path:
            return "❌ Ruta requerida"
        
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return f"❌ Archivo no encontrado: {path}"
        
        if not file_path.is_file():
            return f"❌ No es un archivo: {path}"
        
        try:
            with open(file_path) as f:
                content = f.read()
            
            # Limitar output
            max_lines = kwargs.get("max_lines", 100)
            lines = content.split("\n")
            if len(lines) > max_lines:
                content = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} líneas más)"
            
            return f"📄 {path}\n```\n{content}\n```"
        
        except Exception as e:
            return f"❌ Error al leer: {str(e)}"
    
    def _write(self, path: str, content: str = "", **kwargs) -> str:
        """Escribe un archivo."""
        if not path:
            return "❌ Ruta requerida"
        
        file_path = self._resolve_path(path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content or "")
            
            return f"✅ Escrito: {path}"
        
        except Exception as e:
            return f"❌ Error al escribir: {str(e)}"
    
    def _append(self, path: str, content: str = "", **kwargs) -> str:
        """Agrega a un archivo."""
        if not path:
            return "❌ Ruta requerida"
        
        file_path = self._resolve_path(path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "a") as f:
                f.write(content or "")
            
            return f"✅ Agregado a: {path}"
        
        except Exception as e:
            return f"❌ Error al agregar: {str(e)}"
    
    def _list(self, path: str = ".", **kwargs) -> str:
        """Lista archivos."""
        dir_path = self._resolve_path(path)
        
        if not dir_path.exists():
            return f"❌ Directorio no encontrado: {path}"
        
        files = []
        for item in dir_path.iterdir():
            if item.name.startswith("."):
                continue
            if kwargs.get("all"):
                files.append(f"{'📁' if item.is_dir() else '📄'} {item.name}")
            elif item.is_file():
                files.append(f"📄 {item.name}")
        
        return "\n".join(files) if files else "📭 Directory vacío"
    
    def _delete(self, path: str, **kwargs) -> str:
        """Elimina un archivo."""
        if not path:
            return "❌ Ruta requerida"
        
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return f"❌ No encontrado: {path}"
        
        try:
            file_path.unlink()
            return f"🗑️ Eliminado: {path}"
        except Exception as e:
            return f"❌ Error al eliminar: {str(e)}"
    
    def _exists(self, path: str, **kwargs) -> str:
        """Verifica existencia."""
        if not path:
            return "❌ Ruta requerida"
        
        file_path = self._resolve_path(path)
        
        if file_path.exists():
            return f"✅ Existe: {path}"
        return f"❌ No existe: {path}"
    
    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Acción: read, write, append, list, delete, exists",
                    "enum": ["read", "write", "append", "list", "delete", "exists"]
                },
                "path": {
                    "type": "string",
                    "description": "Ruta del archivo"
                },
                "content": {
                    "type": "string",
                    "description": "Contenido (para write, append)"
                }
            },
            "required": ["action"]
        }


# Instancia global
_file_tool: FileTool | None = None


def get_file_tool(workspace: str | Path | None = None) -> FileTool:
    global _file_tool
    if _file_tool is None:
        _file_tool = FileTool(workspace)
    return _file_tool