# Nodo ESP-IDF (ESP32 + QEMU)

Simulación del ESP32 en QEMU (xtensa) con publicación a ThingsBoard. En QEMU no hay Wi‑Fi; usamos un puente (bridge) que lee `TBTELEMETRY:` por stdout y publica por MQTT desde el host/contenedor.

## Requisitos
- Docker / Docker Compose
- ThingsBoard corriendo (ver `../cloud-thingsboard`)

## Ejecutar (QEMU + bridge)
1) Construir imagen e iniciar servicio de ejecución:
```
docker compose build esp-idf-run
TB_TOKEN=<TU_TOKEN> docker compose up esp-idf-run
```
2) Qué verás en la consola:
- Logs de la app (ESP_LOGx)
- `TBTELEMETRY:{...}` impresos
- Logs del bridge publicando a `v1/devices/me/telemetry`

Notas de arranque:
- El script `tools/run_qemu_bridge.sh` compila, genera `build/flash.bin` (4MB por defecto) y arranca QEMU con `-drive if=mtd` y `-nic user,model=open_eth`.
- Ajusta tamaño con `QEMU_FLASH_MB=2|4|8|16`.
- Si ThingsBoard no está en la misma red docker, usa `TB_HOST=host.docker.internal`.

## Depurar con GDB
```
# Ventana 1: QEMU esperando GDB
DEBUG=1 TB_TOKEN=<TU_TOKEN> docker compose up esp-idf-run

# Ventana 2: adjuntar
docker compose run --rm esp-idf bash -lc "xtensa-esp32-elf-gdb build/tb_thread_node.elf -ex 'target remote :1234'"
```

## Hardware real (Wi‑Fi)
- Desactiva Ethernet (menuconfig: App Options → Use Ethernet… [off])
- Configura SSID/Password en `main/main.c`
- Flashea y monitorea con ESP-IDF en tu host

## Troubleshooting
## Ejecutar 2 nodos (dos consolas)

Comparten el mismo código/imagen, pero usan tokens y directorios de build distintos:

- Consola A:
```
TB_TOKEN=<TOKEN_A> BUILD_DIR=build_a docker compose up esp-idf-run
```

- Consola B (primero compila, luego puedes usar SKIP_BUILD=1 en relanzos):
```
TB_TOKEN=<TOKEN_B> BUILD_DIR=build_b docker compose up esp-idf-run
# Re-lanzar más rápido:
# TB_TOKEN=<TOKEN_B> BUILD_DIR=build_b SKIP_BUILD=1 docker compose up esp-idf-run
```

Tips:
- Ambas instancias pueden apuntar a `TB_HOST=tb` si comparten la red docker con ThingsBoard; si no, usa `host.docker.internal`.
- Puedes parametrizar `QEMU_FLASH_MB` por instancia si quieres aislar memoria/flash.

Alternativa (aislar contenedores con proyectos -p):

- Consola A:
```
docker compose build esp-idf-run
TB_TOKEN=<TOKEN_A> BUILD_DIR=build_a docker compose -p nodeA up esp-idf-run
```

- Consola B:
```
TB_TOKEN=<TOKEN_B> BUILD_DIR=build_b docker compose -p nodeB up esp-idf-run
```

Alternativa efímera (compose run con nombres):
```
TB_TOKEN=<TOKEN_A> BUILD_DIR=build_a docker compose run --rm --name esp32-node-a esp-idf-run
TB_TOKEN=<TOKEN_B> BUILD_DIR=build_b docker compose run --rm --name esp32-node-b esp-idf-run
```


- QEMU: "unsupported machine type: 'esp32'"
	- Asegúrate de usar esta imagen (compila QEMU de Espressif). Reconstruye sin caché:
		- `docker compose build --no-cache esp-idf-run`

- Docker build falla por `gcrypt.h` o `libslirp.h` no encontrado
	- La imagen instala `libgcrypt20-dev`, `libgpg-error-dev`, `libslirp-dev`. Si vienes de capas viejas, fuerza rebuild sin caché.

- Build/export se queda en "exporting to oci image format / sending tarball"
	- Prueba limpiar capas: `docker system prune -af` (cuidado: borra contenedores/imagenes sin usar).
	- Verifica tener espacio en disco y recursos suficientes en Docker Desktop.

- Al correr: "Not initializing SPI Flash" o warning de `-bios`/`-kernel`
	- El script ya genera `build/flash.bin` con dd y arranca con `-drive if=mtd`. Asegúrate de usar el script actualizado.

- Error: "only 2, 4, 8, 16 MB flash images are supported"
	- Usa un tamaño válido de flash: `QEMU_FLASH_MB=4` (o 2/8/16).

- Error: "could not load ELF file 'none'"
	- Indica uso de `-bios none` erróneo. Ya se eliminó del script. Reconstruye la imagen o re-ejecuta con el script actualizado.

- Bridge conecta pero no ves telemetría en ThingsBoard
	- Verifica el Token del dispositivo y que estés mirando el mismo dispositivo en TB.
	- Revisa la consola: deben aparecer `[bridge] published {...}`.
	- En TB, la pestaña de Latest telemetry a veces no auto-refresca: recarga la página.

- MQTT connection refused / timeout
	- ¿ThingsBoard está arriba? `modules/01-arquitectura-iot/cloud-thingsboard: docker compose up -d`.
	- Si el nodo está en otra red/stack, usa `TB_HOST=host.docker.internal` y `TB_PORT=1883`.
	- Revisa firewall/VPN en el host.

- GDB: "Couldn't connect to remote target"
	- Lanza con `DEBUG=1 TB_TOKEN=... docker compose up esp-idf-run` antes de adjuntar GDB a `:1234`.

- Apple Silicon (M1/M2): ThingsBoard no arranca
	- En el compose de ThingsBoard, agrega `platform: linux/amd64` bajo el servicio `tb`.

- Limpiar build de ESP-IDF
	- Dentro del contenedor de desarrollo: `idf.py fullclean` o borra `build/`.

