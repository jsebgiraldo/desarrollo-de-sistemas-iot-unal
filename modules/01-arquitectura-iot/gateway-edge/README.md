# Gateway / Edge Computing

Este componente actúa como gateway para múltiples nodos y realiza procesamiento local (agregación, filtrado, alertas) antes de enviar a ThingsBoard.

## Opción Python
Cliente MQTT (paho-mqtt) simple para gateway.

## Python Quickstart
1) Crear venv e instalar deps:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Ejecutar:
```
TB_HOST=localhost TB_PORT=1883 TB_TOKEN=<token_gateway> python3 src/gateway.py
```

## Node-RED (opcional)
- Si deseas, importa `flows.json` en tu instancia de Node-RED.

## Configuración de ThingsBoard
- Igual que el nodo, usa un dispositivo tipo Gateway en TB y su token correspondiente.
