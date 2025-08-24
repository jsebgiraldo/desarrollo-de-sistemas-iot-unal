# Desarrollo de Sistemas IoT - UNAL

Repositorio del curso de Desarrollo de Sistemas IoT (UNAL). Este repositorio contiene módulos prácticos y documentación para construir sistemas IoT de punta a punta.

## Módulos
- `modules/01-arquitectura-iot/`: Demo de arquitectura IoT (ESP32 + Gateway + ThingsBoard + Cloud).

## Documentación
La documentación paso a paso de cada módulo está en `docs/`.

## Requisitos generales
- macOS/Linux/Windows con Docker y Docker Compose
- Python 3.10+
- Node.js 18+ (opcional para gateway)

## Cómo empezar
1) ThingsBoard (consola):
```
cd modules/01-arquitectura-iot/cloud-thingsboard
docker compose up -d
```
2) Nodo en QEMU (consola):
```
cd ../node-esp-idf
docker compose build esp-idf-run
TB_TOKEN=<token> docker compose up esp-idf-run
```
3) Guía: revisa `docs/` para detalles y dashboards.
