---
name: coder
description: Generación y revisión de código multi-lenguaje
triggers: ["code", "python", "javascript", "编程", "programar", "generar"]
---

# Skill: Coder

Este skill proporciona ayuda para generación y revisión de código.

## Lenguajes soportados

### Python
```python
# Ejemplo de función
def hello(name: str) -> str:
    return f"Hola, {name}!"

# Clase con type hints
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
```

### JavaScript
```javascript
// Función flecha
const hello = (name) => `Hola, ${name}!`;

// Clase
class Calculator {
  add(a, b) {
    return a + b;
  }
}
```

### Bash
```bash
#!/bin/bash
echo "Hola, $1!"
```

## Best practices

1. **Type hints** - Usar type annotations
2. **Docstrings** - Documentar funciones
3. **Tests** - Siempre escribir tests
4. **Linting** - Usar ruff/black para Python
5. **ESLint** - Para JavaScript