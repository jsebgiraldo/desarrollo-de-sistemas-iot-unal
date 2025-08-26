# Nodo ESP32/QEMU (ESP-IDF)

Simula un nodo ESP32 ejecutando firmware real en QEMU y publicando telemetría a ThingsBoard.

## Requisitos
- Docker / Docker Compose
- Token de dispositivo en ThingsBoard (ver [README del servidor](../cloud-thingsboard/README.md))

## Cómo ejecutar
```bash
docker compose build esp-idf-run
TB_TOKEN=<TU_TOKEN> docker compose up esp-idf-run
```
Verás en la consola:
- Logs de la app (ESP_LOGx)
- `TBTELEMETRY:{...}` impresos
- Logs del bridge publicando a `v1/devices/me/telemetry`

## Notas y troubleshooting
- El script `tools/run_qemu_bridge.sh` compila, genera `build/flash.bin` (4MB por defecto) y arranca QEMU con `-drive if=mtd` y `-nic user,model=open_eth`.
- Ajusta tamaño con `QEMU_FLASH_MB=2|4|8|16`.
- Si ThingsBoard no está en la misma red docker, usa `TB_HOST=host.docker.internal`.
- Para simular varios nodos, usa diferentes tokens y directorios de build:
	```bash
	TB_TOKEN=<TOKEN_A> BUILD_DIR=build_a docker compose up esp-idf-run
	TB_TOKEN=<TOKEN_B> BUILD_DIR=build_b docker compose up esp-idf-run
	```
- Para debugging con GDB:
	- Ventana 1: `DEBUG=1 TB_TOKEN=<TU_TOKEN> docker compose up esp-idf-run`
	- Ventana 2: `docker compose run --rm esp-idf bash -lc "xtensa-esp32-elf-gdb build/tb_thread_node.elf -ex 'target remote :1234'"`
- Si ThingsBoard no arranca en Apple Silicon, agrega `platform: linux/amd64` bajo el servicio `tb` en el compose.


