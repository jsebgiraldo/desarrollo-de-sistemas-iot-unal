
# Guía: Práctica Arquitectura IoT (Servidor, Gateway y Nodos)

Esta guía te permite reproducir una arquitectura IoT completa usando ThingsBoard CE, el gateway oficial, Mosquitto y nodos simulados.

## 1) Servidor ThingsBoard
1. Ve a `modules/01-arquitectura-iot/cloud-thingsboard`
2. Levanta el servidor:
  ```bash
  docker compose up -d
  ```
3. Accede a http://localhost:8080
  - Inicia sesión como SysAdmin: `sysadmin@thingsboard.org` / `sysadmin`
  - Crea un Tenant y un dispositivo tipo Gateway. Copia su Token.

## 2) Gateway oficial + Mosquitto
1. Ve a `modules/01-arquitectura-iot/gateway-edge`
2. Levanta Mosquitto (broker MQTT):
  ```bash
  docker compose -f docker-compose.external.yml up -d mosquitto
  ```
3. Levanta el gateway oficial:
  ```bash
  docker compose -f docker-compose.tbgw.yml up -d
  ```
4. En el UI de ThingsBoard (Gateway → Connectors → MQTT), configura:
  - Host: 127.0.0.1
  - Port: 1884
  - MQTT version: 5
  - Client ID: ThingsBoard_gateway
  - Security: Anonymous

## 3) Nodos simulados
1. Desde la misma carpeta (`gateway-edge`):
  ```bash
  docker compose -f docker-compose.devices.yml up -d
  ```
2. Los simuladores publican:
  - Conexión: `sensor/connect` con `{ "serialNumber": "sim-node-1" }` y `sim-node-2`.
  - Telemetría: `sensor/data` con `{ "device": "sim-node-1|2", "temperature": .., "humidity": .. }`.

## 4) Validación
- En ThingsBoard, ve a tu Gateway → pestaña Child devices: deben aparecer sim-node-1 y sim-node-2.
- Latest telemetry: temperature y humidity actualizándose.

## 5) (Opcional) Nodo ESP32/QEMU
1. Ve a `modules/01-arquitectura-iot/node-esp-idf`
2. Construye y ejecuta:
  ```bash
  docker compose build esp-idf-run
  TB_TOKEN=<token> docker compose up esp-idf-run
  ```
3. Verifica telemetría en ThingsBoard → Device → Latest telemetry.
  - Si no estás en la misma red, usa `TB_HOST=host.docker.internal`.

## Limpieza
```bash
docker compose -f modules/01-arquitectura-iot/gateway-edge/docker-compose.devices.yml down
docker compose -f modules/01-arquitectura-iot/gateway-edge/docker-compose.tbgw.yml down
docker compose -f modules/01-arquitectura-iot/gateway-edge/docker-compose.external.yml down
cd modules/01-arquitectura-iot/cloud-thingsboard && docker compose down -v
```

## Notas
- Si usas Apple Silicon y ThingsBoard no arranca, agrega `platform: linux/amd64` bajo el servicio `tb` en el compose.
- Para debugging del nodo ESP32/QEMU: `DEBUG=1 TB_TOKEN=<token> docker compose up esp-idf-run` y adjunta GDB (`xtensa-esp32-elf-gdb build/tb_thread_node.elf -ex 'target remote :1234'`).
