# Módulo 01: Arquitectura IoT (Gateway + Mosquitto + ThingsBoard)

Arquitectura de referencia para el curso: dispositivos publican a un broker local (Mosquitto), el Gateway oficial de ThingsBoard consume esos tópicos y reenvía como child devices al servidor ThingsBoard.

## Componentes
- `cloud-thingsboard/`: ThingsBoard CE en Docker (UI en http://localhost:8080).
- `gateway-edge/`: 
	- `docker-compose.tbgw.yml`: Gateway oficial (thingsboard/tb-gateway).
	- `docker-compose.external.yml`: Mosquitto (broker de borde) y gateway Python opcional (legacy).
	- `docker-compose.devices.yml`: simuladores MQTT.
- `node-esp-idf/` (opcional): ESP32/QEMU publicando directo a ThingsBoard (sin gateway).
- `docs/`: guía de laboratorio.
 - `practica-01/`: guía integrada y reproducible para la práctica 01.

## Requisitos
- Docker y Docker Compose.
- Token de un dispositivo Gateway creado en ThingsBoard.

## Pasos del laboratorio (reproducibles)
1) Levantar ThingsBoard
```
cd cloud-thingsboard
docker compose up -d
```
2) Levantar Mosquitto (broker edge)
```
cd ../gateway-edge
docker compose -f docker-compose.external.yml up -d mosquitto
```
3) Levantar Gateway oficial
```
docker compose -f docker-compose.tbgw.yml up -d
```
En el UI del Gateway (ThingsBoard → tu Gateway → Connectors → MQTT):
- Host: 127.0.0.1
- Port: 1884
- MQTT version: 5
- Client ID: ThingsBoard_gateway
- Security: Anonymous

4) Arrancar simuladores
```
docker compose -f docker-compose.devices.yml up -d
```
Publican:
- Conexión: `sensor/connect` con `{"serialNumber":"sim-node-1"}` y `sim-node-2`.
- Telemetría: `sensor/data` con `{"device":"sim-node-1|2","temperature":..,"humidity":..}`.

5) Verificar en ThingsBoard
- En tu dispositivo Gateway → pestaña Child devices: aparecen sim-node-1 y sim-node-2.
- Latest telemetry muestra temperature y humidity.

## Variante: ESP32/QEMU (opcional)
Sigue `node-esp-idf/README.md` para publicar directo a ThingsBoard con token de dispositivo.

## Limpieza
```
docker compose -f docker-compose.devices.yml down
docker compose -f docker-compose.tbgw.yml down
docker compose -f docker-compose.external.yml down
cd ../cloud-thingsboard && docker compose down -v
```

## Troubleshooting
- Gateway no ve a Mosquitto:
	- Si configuraste Host=127.0.0.1 y el gateway está en contenedor, 127.0.0.1 apunta al contenedor. Usa 127.0.0.1:1884 (puerto expuesto del host) o configura por archivo a `mosquitto:1883`.
- Dispositivos no aparecen:
	- Asegura que publican a `sensor/connect` y `sensor/data` con el `device` correcto.
- Token inválido del Gateway:
	- Ver logs del gateway y confirmar token del dispositivo de tipo Gateway.
