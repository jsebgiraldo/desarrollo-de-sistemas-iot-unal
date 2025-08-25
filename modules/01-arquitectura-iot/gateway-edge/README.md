## Gateway / Edge Computing

Este directorio contiene dos enfoques:
- Gateway oficial de ThingsBoard (recomendado) + Mosquitto + simuladores.
- Gateway Python (legacy) para fines didácticos.

## ¿Por qué es importante el Gateway?
- Agrega y normaliza datos de varios nodos sin que cada uno conozca la nube.
- Reduce costos de conectividad y latencia (procesando en el borde: filtros, promedios, umbrales).
- Aísla protocolos locales (BLE, Zigbee, Modbus) y los traduce a MQTT/HTTP para la nube.
- Administra hijos: conexión/desconexión, atributos, RPC y seguridad centralizada.

## Requisitos
- Python 3.8+
- ThingsBoard CE/PE accesible por MQTT (puerto 1883)
- Crear en ThingsBoard un dispositivo de tipo Gateway y obtener su Token

## Opción recomendada: Gateway oficial + Mosquitto

Servicios y archivos clave:
- `docker-compose.external.yml`: levanta Mosquitto (expuesto en 1884).
- `docker-compose.tbgw.yml`: levanta el contenedor thingsboard/tb-gateway.
- `docker-compose.devices.yml`: simuladores que publican al broker en 1884.

## Instalación rápida
1) Crear venv e instalar deps:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Configurar hijos (opcional):
- Edita `devices.json` o usa `GW_CHILDREN="node-1,node-2"`. Por defecto ya se cargan `node-1` y `node-2`.
3) Ejecutar el gateway:
```
TB_HOST=localhost TB_PORT=1883 TB_TOKEN=<token_gateway> \
GW_CHILDREN_FILE=./devices.json GW_PERIOD_SEC=5 \
python3 src/gateway.py
```

### Ejecutar con Docker / Docker Compose

Opción A: levantar TB y el gateway juntos (compose en esta carpeta)
```
cd modules/01-arquitectura-iot/gateway-edge
export TB_TOKEN=<token_gateway>
docker compose up --build
```
- Accede a TB en http://localhost:8080 y verifica los child devices.

Opción B: si ya tienes TB corriendo en `cloud-thingsboard` y quieres unir el gateway a esa red:
1) Levanta TB:
```
cd modules/01-arquitectura-iot/cloud-thingsboard
docker compose up -d
```
2) Construye la imagen del gateway y conéctalo a la red `tbnet`:
```
cd ../gateway-edge
docker build -t tb-gateway:local .
docker run --rm --name tb-gateway \
	--network cloud-thingsboard_tbnet \
	-e TB_HOST=tb -e TB_PORT=1883 -e TB_TOKEN=<token_gateway> \
	-e GW_CHILDREN_FILE=/app/devices.json -e GW_PERIOD_SEC=5 \
	-v $(pwd)/devices.json:/app/devices.json:ro \
	tb-gateway:local
```
Nota: el nombre de la red puede verse como `cloud-thingsboard_tbnet` si usas Docker Compose v2 con nombre de proyecto.

Al iniciar, el gateway:
- Se conecta con el token del dispositivo Gateway.
- Conecta/declara a sus hijos en `v1/gateway/connect` y publica atributos iniciales en `v1/gateway/attributes`.
- Envía telemetría de cada hijo a `v1/gateway/telemetry` cada `GW_PERIOD_SEC` segundos.
- Escucha y responde RPCs básicos en `v1/gateway/rpc` (eco del payload).

## Conector MQTT integrado (para que cada nodo publique por MQTT al gateway)
El gateway incluye un broker MQTT local (Mosquitto) y un conector que traduce tópicos locales a la API de ThingsBoard.

Tópicos de publicación por parte de los nodos (en el broker del gateway):
- Telemetría: `devices/<deviceName>/telemetry`
	- Payload aceptado:
		- Forma simple: `{ "temperature": 23.5, "humidity": 60 }`
		- Con timestamp: `{ "ts": 1710000000000, "values": { "temperature": 23.5 } }`
- Atributos cliente: `devices/<deviceName>/attributes`
	- Payload: `{ "fw": "1.0.0", "location": "lab" }`
- RPC respuesta (cuando TB envía un RPC): `devices/<deviceName>/rpc/response/<requestId>`
	- Payload: cualquier JSON, el conector lo reenvía a TB como respuesta.

RPC desde ThingsBoard hacia el nodo:
- TB envía al gateway y éste reenviará a `devices/<deviceName>/rpc/request/<requestId>` con el `data` del RPC como payload.

Variables de entorno del conector:
- `GW_SIMULATE_CHILDREN`: `false` para usar solo el conector (sin telemetría simulada).
- `CONNECTOR_MQTT_ENABLE`: `true|false`.
- `CONNECTOR_MQTT_HOST`, `CONNECTOR_MQTT_PORT`: broker local (por defecto `mosquitto:1883`).
- `CONNECTOR_TOPIC_PREFIX`: prefijo de tópicos (por defecto `devices`).

## Práctica para el Módulo 1 (integración con Cloud)
Objetivo: que el estudiante vea el patrón Gateway con múltiples hijos en ThingsBoard.

Pasos sugeridos:
1) En TB, crear un dispositivo de tipo Gateway y copiar el Token.
2) Clonar e instalar este módulo como arriba.
3) Ejecutar el gateway con el Token de TB.
4) En TB, verificar:
	- El Gateway aparece online (atributos/telemetría del gateway).
	- En la sección del Gateway → Child devices, aparecen `node-1`, `node-2`.
	- Ver telemetría de los hijos en dashboards o en Latest telemetry.
5) Extensiones:
	- Editar `devices.json` y agregar `node-3` con valores iniciales. Reiniciar el gateway y verificar que se registre y publique.
	- Modificar `src/gateway.py` para emitir una alerta local (atributo `edge_alert=true`) si `temperature > 26`.
	- Probar un RPC: enviar desde TB un RPC a `node-1` y observar la respuesta eco en logs y en TB.

## Node-RED (opcional)
- Puedes importar `flows.json` en Node-RED para experimentar con ingesta/transformación alternativa.

## Variables de entorno
- `TB_HOST`: host/IP de ThingsBoard (por defecto `localhost`).
- `TB_PORT`: puerto MQTT (por defecto `1883`).
- `TB_TOKEN`: token del dispositivo Gateway en TB.
- `GW_CHILDREN_FILE`: ruta a `devices.json` con los hijos y valores iniciales.
- `GW_CHILDREN`: lista separada por comas de hijos a simular (si no hay archivo), ej. `node-1,node-2,node-3`.
- `GW_PERIOD_SEC`: periodo de publicación de telemetría (segundos, por defecto `5`).

## Formatos de la API de ThingsBoard Gateway (MQTT)
- Conexión de hijo: topic `v1/gateway/connect` con payload `{ "device": "child-1" }`.
- Telemetría: topic `v1/gateway/telemetry` con payload `{ "child-1": [{"ts": 1710000000000, "values": {"t": 23}}] }`.
- Atributos: topic `v1/gateway/attributes` con payload `{ "device": "child-1", "attributes": {"k": "v"} }`.
- RPC: topic `v1/gateway/rpc` (bidireccional). Este ejemplo hace eco del `data` recibido.

## Opción legacy: Gateway Python

Archivos:
- `Dockerfile`, `src/gateway.py`, `devices.json`.

Ejecución (solo si deseas estudiar la API v1/gateway):
```
export TB_TOKEN=<token_gateway>
docker compose -f docker-compose.external.yml up -d
docker logs -f tb-gateway
```

## Limpieza
```
docker compose -f docker-compose.devices.yml down
docker compose -f docker-compose.tbgw.yml down
docker compose -f docker-compose.external.yml down
```

## Troubleshooting
- Si configuraste 127.0.0.1:1884 en el conector del gateway y no recibes datos, asegúrate de que el gateway corre en la misma máquina del broker y que 1884 está expuesto.
- Alternativa por archivo: configura `tbgw-config/mqtt.json` para apuntar a `mosquitto:1883` (misma red Docker) y desactiva `remoteConfiguration` en `tb_gateway.json`.
