---
name: automation
description: Templates para automatización y scripts
triggers: ["automation", "script", "cron", "automation", "scheduled", "tarea"]
---

# Skill: Automation

Este skill proporciona templates para automatización.

## Cron

### Formato
```
┌───────────── minuto (0 - 59)
│ ┌───────────── hora (0 - 23)
│ │ ┌───────────── día del mes (1 - 31)
│ │ │ ┌───────────── mes (1 - 12)
│ │ │ │ ┌───────────── día de la semana (0 - 6) (Domingo=0)
│ │ │ │ │
* * * * *
```

### Ejemplos
```bash
# Cada hora
0 * * * *

# Diario a las 9 AM
0 9 * * *

# Monday a las 9 AM
0 9 * * 1

# Cada 15 minutos
*/15 * * * *
```

## Script template

```bash
#!/bin/bash
set -euo pipefail

LOGFILE="/var/log/mi-script.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

main() {
    log "Iniciando script..."
    # Tu código aquí
    log "Completado"
}

main "$@"
```

## Python script

```python
#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando...")
    # Tu código aquí
    logger.info("Completado")

if __name__ == "__main__":
    main()
```