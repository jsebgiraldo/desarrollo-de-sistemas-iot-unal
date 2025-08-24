# Guía: Demo Arquitectura IoT

Objetivo: levantar ThingsBoard local, ejecutar el nodo ESP-IDF en QEMU con puente a MQTT, y opcionalmente un gateway, para visualizar telemetría.

## 1) Servidor ThingsBoard
- Ir a `modules/01-arquitectura-iot/cloud-thingsboard`
- `docker compose up -d`
- Abrir http://localhost:8080, crear Tenant y Dispositivo, copiar Token.

## 2) Nodo ESP-IDF + QEMU
- Ir a `modules/01-arquitectura-iot/node-esp-idf`
- Construir y ejecutar:
  - `docker compose build esp-idf-run`
  - `TB_TOKEN=<token> docker compose up esp-idf-run`
- Ver en ThingsBoard → Device → Latest telemetry.
  - Si no estás en la misma red, usa `TB_HOST=host.docker.internal`.
  - El script crea `build/flash.bin` y arranca QEMU con `-drive if=mtd` y `-nic user,model=open_eth`.

## 3) Gateway (opcional)
- Instala deps: en `gateway-edge`: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
- Ejecuta: `TB_HOST=localhost TB_PORT=1883 TB_TOKEN=<token_gateway> python3 src/gateway.py`

Notas
- Depuración: `DEBUG=1 TB_TOKEN=<token> docker compose up esp-idf-run` y adjunta GDB (`xtensa-esp32-elf-gdb build/tb_thread_node.elf -ex 'target remote :1234'`).
- Apple Silicon: si TB falla por arquitectura, usa `platform: linux/amd64` en su compose.
