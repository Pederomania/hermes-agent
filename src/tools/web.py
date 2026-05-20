"""Herramienta de búsqueda web."""
import os
from typing import Any

from .base import Tool, ToolResult


class WebSearchTool(Tool):
    """Búsqueda web usando Tavily."""
    
    name = "web_search"
    description = "Busca información en la web y retorna resultados relevantes"
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
    
    def execute(self, query: str, max_results: int = 5, **kwargs) -> str:
        """Busca en la web."""
        if not self.api_key:
            return f"❌ TAVILY_API_KEY no configurada. Busca no disponible para: {query}"
        
        return self._fetch_with_tavily(query, max_results)
    
    def _fetch_with_tavily(self, query: str, max_results: int) -> str:
        """Busca usando Tavily API."""
        try:
            import requests
            
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,  # Incluir la API key
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return self._format_fallback(query, max_results)
            
            data = response.json()
            return self._format_results(data)
        
        except Exception:
            return self._format_fallback(query, max_results)
    
    def _format_fallback(self, query: str, max_results: int) -> str:
        """Fallback simple si Tavily no está disponible."""
        return f"Búsqueda: {query}\n\n(No se pudo conectar a Tavily. Configura TAVILY_API_KEY para habilitar búsqueda web)"
    
    def _format_results(self, data: dict) -> str:
        """Formatea resultados."""
        results = data.get("results", [])
        answer = data.get("answer", "")
        
        output = []
        if answer:
            output.append(f"📌 {answer}\n")
        
        output.append("📄 Resultados:")
        for i, r in enumerate(results, 1):
            title = r.get("title", "Sin título")
            url = r.get("url", "")
            content = r.get("content", "")[:200]
            
            output.append(f"\n{i}. {title}")
            output.append(f"   {url}")
            output.append(f"   {content}...")
        
        return "\n".join(output)
    
    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query de búsqueda"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Máximo de resultados (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }


# Instancia global
_web_search_tool: WebSearchTool | None = None


def get_web_search_tool(api_key: str | None = None) -> WebSearchTool:
    global _web_search_tool
    if _web_search_tool is None:
        _web_search_tool = WebSearchTool(api_key)
    return _web_search_tool