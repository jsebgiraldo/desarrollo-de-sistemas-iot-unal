
# Gateway oficial ThingsBoard + Mosquitto + Simuladores

Este directorio contiene todo lo necesario para reproducir el ejemplo de gateway IoT con ThingsBoard, Mosquitto y nodos simulados.

## Arquitectura
- **Mosquitto**: broker MQTT local, expone el puerto 1884 en el host para que los dispositivos/simuladores publiquen.
- **Gateway oficial**: contenedor thingsboard/tb-gateway, conecta a Mosquitto y reenvía datos a ThingsBoard como child devices.
- **Simuladores**: publican a `sensor/connect` y `sensor/data` en Mosquitto, aparecen como child devices en el Gateway.

## Ejemplo reproducible (paso a paso)

### 1. Levantar Mosquitto (broker MQTT)
```bash
docker compose -f docker-compose.external.yml up -d mosquitto
```
Expone 1884 en el host.

### 2. Levantar el Gateway oficial de ThingsBoard
```bash
docker compose -f docker-compose.tbgw.yml up -d
```
Configura el conector MQTT en el UI del Gateway (ThingsBoard → tu Gateway → Connectors → MQTT):
- Host: 127.0.0.1
- Port: 1884
- MQTT version: 5
- Client ID: ThingsBoard_gateway
- Security: Anonymous

### 3. Levantar los simuladores de nodos
```bash
docker compose -f docker-compose.devices.yml up -d
```
Publican:
- Conexión: `sensor/connect` con `{ "serialNumber": "sim-node-1" }` y `sim-node-2`.
- Telemetría: `sensor/data` con `{ "device": "sim-node-1|2", "temperature": .., "humidity": .. }`.

### 4. Validación
- En ThingsBoard, ve a tu Gateway → pestaña Child devices: deben aparecer sim-node-1 y sim-node-2.
- Latest telemetry: temperature y humidity actualizándose.

## Limpieza
```bash
docker compose -f docker-compose.devices.yml down
docker compose -f docker-compose.tbgw.yml down
docker compose -f docker-compose.external.yml down
```

## Troubleshooting
- Si configuraste 127.0.0.1:1884 en el conector del gateway y no recibes datos, asegúrate de que el gateway corre en la misma máquina del broker y que 1884 está expuesto.
- Alternativa por archivo: configura `tbgw-config/mqtt.json` para apuntar a `mosquitto:1883` (misma red Docker) y desactiva `remoteConfiguration` en `tb_gateway.json`.
