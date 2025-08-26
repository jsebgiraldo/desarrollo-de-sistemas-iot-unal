
# ThingsBoard CE (Docker)

Servidor IoT open source para ingesta, visualización y gestión de dispositivos.

## Cómo levantar el servidor
```bash
docker compose up -d
```
Accede a http://localhost:8080
- Inicia sesión como SysAdmin: `sysadmin@thingsboard.org` / `sysadmin`.
- Crea un Tenant y un Tenant Admin.
- Ingresa con el Tenant Admin y crea un Dispositivo (tipo Gateway). Copia su Token.

## Limpieza
```bash
docker compose down -v
```

## Notas y troubleshooting
- Persistencia en volúmenes `tb-data`, `tb-logs`.
- Si en Apple Silicon hay error de arquitectura, agrega:
   ```yaml
   platform: linux/amd64
   ```
   bajo el servicio `tb` en el compose.
- La red `tbnet` permite que otros contenedores accedan por host `tb`. Si ejecutas servicios en otra carpeta/compose, únelos a `cloud-thingsboard_tbnet` o usa `host.docker.internal` como host.

