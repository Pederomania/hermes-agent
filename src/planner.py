"""Planner: decide las acciones a tomar."""
import json
from typing import Any

from src.config import get_config
from src.memory.db import Memory
from src.tools import get_all_schemas


class Planner:
    """Planificador que decide los próximos pasos."""
    
    def __init__(self, provider=None, memory: Memory = None):
        self.provider = provider
        self.memory = memory
        self.config = get_config()
        self._system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema con tools disponibles."""
        schemas = get_all_schemas()
        
        tools_text = []
        for tool in schemas:
            tools_text.append(f"""
### {tool['name']}
{tool['description']}
Params: {json.dumps(tool['parameters'], indent=2)}
""")
        
        return f"""Eres el Planner de un agente autónomo tipo Hermes.

## Tu rol
Analizar la situación actual, decidir el siguiente paso, y planear cómo ejecutarlo.

## Herramientas disponibles
{chr(10).join(tools_text)}

## Directrices
1. Solo decide una accion a la vez
2. Analiza el output de la accion anterior
3. Si fallo, replanifica
4. Si tienes exito, continuar al siguiente paso
5. Siempre devuelve un plan estructurado en JSON

## Output
Cada accion debe devolver en JSON:
```json
{
  "thought": "tu razonamiento",
  "action": "nombre de tool a usar",
  "args": {"arg1": "valor1"},
  "reasoning": "por que esta accion"
}
```

Ahora analiza la situacion y decide:"""
    
    def plan(self, goal: str, context: str = "", last_result: str = "") -> dict:
        """
        Decide el siguiente paso.
        
        Args:
            goal: Goal principal
            context: Contexto de la conversación
            last_result: Resultado de la última action
        
        Returns:
            Dict con thought, action, args, reasoning
        """
        # Build messages
        messages = [
            {"role": "system", "content": self._system_prompt}
        ]
        
        # Add context if available
        if context:
            messages.append({"role": "user", "content": f"Contexto: {context}"})
        
        # Add last result if available
        if last_result:
            messages.append({
                "role": "user", 
                "content": f"Resultado de la última action:\n{last_result}\n\n¿Cuál es el siguiente paso?"
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Goal: {goal}\n\nDecide la primera action a tomar."
            })
        
        # Call LLM
        response = self.provider.chat(messages)
        
        # Parse response
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        """Parsea la response del LLM."""
        try:
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: return as text action
        return {
            "thought": response[:200],
            "action": "echo",
            "args": {"message": response},
            "reasoning": "Response del modelo"
        }
    
    def should_continue(self, goal: str, result: str) -> bool:
        """
        Decide si debemos continuar o terminado.
        
        Args:
            goal: Goal original
            result: Resultado reciente
        
        Returns:
            True si debe continuar, False si terminado
        """
        prompt = f"""Analiza si se ha cumplido el objetivo.

Goal: {goal}
Resultado: {result}

Responde SOLO con "sí" o "no":"""
        
        response = self.provider.complete(prompt).lower().strip()
        return "sí" in response or "si" in response


# Instancia global
_planner: Planner | None = None


def get_planner(provider=None, memory: Memory = None) -> Planner:
    """Obtiene el planner."""
    global _planner
    if _planner is None:
        _planner = Planner(provider, memory)
    return _planner