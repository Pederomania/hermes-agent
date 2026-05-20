---
name: sysadmin
description: Helper de administración de sistemas Linux/SSH
triggers: ["sysadmin", "linux", "ssh", "system", "server", "admin"]
---

# Skill: Sysadmin

Este skill proporciona comandos útiles para administración de sistemas.

## Comandos comunes

### Información del sistema
```bash
# uptime y carga
uptime

# memoria
free -h

# disco
df -h

# procesos
ps aux | head -20

#top procesos
top -bn1 | head -15
```

### Servicios
```bash
# Estado de servicio
systemctl status nginx

# Reiniciar servicio
sudo systemctl restart nginx

# Ver logs
journalctl -u nginx --no-pager -n 50
```

### Red
```bash
# Puertos abiertos
ss -tulpn

# Conexiones
netstat -tuln

# Firewall
sudo ufw status
```

### archivos
```bash
# Últimos archivos modificados
find /var -type f -mtime -1 | head -20

# Tamaño de directorios
du -sh */
```