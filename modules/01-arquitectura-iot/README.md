# Módulo 01: Arquitectura IoT

Este módulo demuestra una arquitectura IoT completa:
- Nodo (ESP32 con ESP-IDF) publicando telemetría.
- QEMU para simulación de firmware sin hardware, usando un bridge MQTT.
- Gateway/Edge (opcional) para agregación/procesamiento local.
- Servidor IoT (ThingsBoard) para ingesta, visualización y reglas.

## Estructura
- `node-esp-idf/`: ejemplo con ESP-IDF (ESP32), Docker y QEMU + bridge.
- `gateway-edge/`: servicio Python para actuar como gateway (opcional).
- `cloud-thingsboard/`: despliegue local con Docker de ThingsBoard CE.
- `docs/`: documentación guiada del laboratorio.

## Requisitos generales
- Docker y Docker Compose (para ThingsBoard y entorno ESP-IDF).
- Python 3.10+ (para scripts de gateway y utilidades).
- Node.js 18+ (opcional para Node-RED u otros clientes).

Nota: no se requieren tareas de VS Code; ejecuta todo desde la consola siguiendo los README.

## Flujo del demo
1. Levantar ThingsBoard CE en local con Docker.
2. Registrar un dispositivo (ESP32) y obtener su token de acceso.
3. Compilar el nodo ESP-IDF y ejecutar en QEMU (bridge) para validar lógica. Puedes correr dos nodos simultáneamente con diferentes tokens (ver sección en `node-esp-idf/README.md`).
4. Opcional: Gateway lee múltiples nodos (o simula nodos), agrega datos y publica a ThingsBoard.
5. Crear dashboard en ThingsBoard para visualizar datos y reglas simples.

## Cómo usar
Sigue las guías en cada subcarpeta y en `docs/01-arquitectura-iot`.
