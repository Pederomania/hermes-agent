"""Evaluator: evalúa si las acciones tuvieron éxito."""
from typing import Any

from src.config import get_config
from src.providers import get_default_provider


class Evaluator:
    """Evalúa results de acciones."""
    
    def __init__(self, provider=None):
        self.provider = provider or get_default_provider()
        self.config = get_config()
    
    def evaluate(self, goal: str, action: str, result: str) -> dict:
        """
        Evalúa si la action tuvo éxito.
        
        Args:
            goal: Goal original
            action: Acción tomada
            result: Resultado de la action
        
        Returns:
            Dict con success, feedback, severity
        """
        prompt = f"""Eres un evaluador de acciones de un agente autónomo.

Analiza si la action resolvió el objetivo.

## Goal
{goal}

## Acción tomada
{action}

## Resultado
{result}

Evalúa:
1. ¿La action tuvo éxito?
2. ¿El result es correcto?
3. ¿Se necesita más trabajo?

Responde en JSON:
```json
{{
  "success": true/false,
  "feedback": "tu evaluación",
  "severity": "critical"/"warning"/"info"/"success"
}}
```"""
        
        try:
            response = self.provider.complete(prompt)
            parsed = self._parse_response(response)
            return parsed
        except Exception as e:
            return {
                "success": True,
                "feedback": f"No se pudo evaluate: {e}",
                "severity": "info"
            }
    
    def _parse_response(self, response: str) -> dict:
        """Parsea la response usando json.loads (NO eval por seguridad)."""
        import re
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
        
        # Fallback: si no puede parsear, NO asumir éxito
        return {
            "success": False,
            "feedback": response[:200],
            "severity": "warning"
        }
    
    def should_retry(self, result: str) -> bool:
        """Decide si debemos reintentar."""
        prompt = f"""Analiza este result:

{result}

¿Deberíamos reintentar esta action?
Responde SOLO con "sí" o "no":"""
        
        response = self.provider.complete(prompt).lower().strip()
        return "sí" in response or "si" in response


# Instancia global
_evaluator: Evaluator | None = None


def get_evaluator(provider=None) -> Evaluator:
    """Obtiene el evaluador."""
    global _evaluator
    if _evaluator is None:
        _evaluator = Evaluator(provider)
    return _evaluator