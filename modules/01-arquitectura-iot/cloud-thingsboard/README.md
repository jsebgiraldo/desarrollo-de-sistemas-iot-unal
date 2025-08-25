# ThingsBoard CE (Docker)

## Levantar el servidor
1. Instala Docker Desktop.
2. En esta carpeta, ejecuta:
   - `docker compose up -d`
3. Abre http://localhost:8080
   - Inicia sesión como SysAdmin: `sysadmin@thingsboard.org` / `sysadmin`.
   - Crea un Tenant y un Tenant Admin.
   - Ingresa con el Tenant Admin y crea un Dispositivo (tipo default). Copia su Token.

Notas:
- Persistencia en volúmenes `tb-data`, `tb-logs`.
- Si en Apple Silicon hay error de arquitectura, agrega:
  ```yaml
  platform: linux/amd64
  ```
  bajo el servicio `tb` en el compose.
- La red `tbnet` permite que otros contenedores accedan por host `tb`. Si ejecutas servicios en otra carpeta/compose, únelos a `cloud-thingsboard_tbnet` o usa `host.docker.internal` como host.

## Limpieza
```
docker compose down -v
```

