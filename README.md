# Desarrollo de Sistemas IoT - UNAL

Repositorio del curso de Desarrollo de Sistemas IoT (UNAL). Incluye un demo completo con servidor IoT (ThingsBoard), gateway oficial, broker MQTT local (Mosquitto) y nodos simulados.

## Módulos
- `modules/01-arquitectura-iot/`: Arquitectura IoT (Gateway + Mosquitto + Simuladores + ThingsBoard). También incluye un ejemplo opcional con ESP32/QEMU.
	- Práctica integrada: `modules/01-arquitectura-iot/practica-01/`

## Documentación
- Guías paso a paso en `docs/`.

## Requisitos generales
- Linux/macOS/Windows con Docker y Docker Compose.
- Opcional: Python 3.10+ (scripts) y ESP-IDF (si usas el ejemplo ESP32 real).

## Quickstart (todas las capas)
1) ThingsBoard CE
```
cd modules/01-arquitectura-iot/cloud-thingsboard
docker compose up -d
```
Accede a http://localhost:8080 y crea un dispositivo de tipo Gateway (copiar token).

2) Mosquitto (broker de borde)
```
cd ../gateway-edge
docker compose -f docker-compose.external.yml up -d mosquitto
```
Expone 1884 (host) → 1883 (contenedor).

3) Gateway oficial de ThingsBoard
```
docker compose -f docker-compose.tbgw.yml up -d
```
Configura el conector MQTT (en el UI del Gateway) a:
- Host: 127.0.0.1
- Port: 1884
- MQTT version: 5
- Client ID: ThingsBoard_gateway
- Security: Anonymous

4) Nodos simulados
```
docker compose -f docker-compose.devices.yml up -d
```
Publican a `sensor/connect` y `sensor/data` en 127.0.0.1:1884. En ThingsBoard, verás los child devices bajo tu Gateway.

5) Ver dashboards
- Crea un dashboard sencillo con time-series de temperature/humidity o usa “Latest telemetry”.

Notas
- El ejemplo ESP32/QEMU es opcional y publica directo a ThingsBoard (no pasa por el gateway). Ver `modules/01-arquitectura-iot/node-esp-idf/`.
- Si usas configuración por archivo para el gateway oficial, ajusta `gateway-edge/tbgw-config/*` en vez del UI.
