#!/usr/bin/env bash
set -euo pipefail

# 1) Cargar entorno ESP-IDF y compilar (Xtensa ESP32)
. /opt/esp/idf/export.sh
idf.py set-target esp32
idf.py build

# 2) Venv para el bridge e instalación de deps
if [ ! -d /opt/pytools ]; then
  python3 -m venv /opt/pytools
fi
# shellcheck disable=SC1091
. /opt/pytools/bin/activate || true
pip install --disable-pip-version-check --no-color -r tools/requirements.txt >/dev/null

# 3) Ejecutar QEMU y encadenar el bridge (salida sin buffer)
export PYTHONUNBUFFERED=1
# Tip: para depurar QEMU, puedes añadir: -d unimp,guest_errors
# Soporta modo debug con DEBUG=1 o QEMU_GDB=1 o argumento --debug (QEMU espera GDB en :1234)
DEBUG_FLAG=${DEBUG:-0}
if [ "${1:-}" = "--debug" ] || [ "${QEMU_GDB:-0}" = "1" ]; then
  DEBUG_FLAG=1
fi

QEMU_OPTS=( -nographic -M esp32 )
if [ "$DEBUG_FLAG" = "1" ]; then
  echo "[run] QEMU en modo debug: esperando GDB en :1234 (usa: xtensa-esp32-elf-gdb build/tb_thread_node.elf -ex 'target remote :1234')"
  QEMU_OPTS+=( -S -s )
fi

# Construir imagen de SPI flash al estilo flash.sh (dd) y arrancar desde ella
BOOT=build/bootloader/bootloader.bin
PART=build/partition_table/partition-table.bin
APPBIN=build/tb_thread_node.bin
FLASHIMG=build/flash.bin

FLASH_MB=${QEMU_FLASH_MB:-4}
case "$FLASH_MB" in
  2|4|8|16) : ;;
  *) echo "[run] QEMU_FLASH_MB inválido '$FLASH_MB', usando 4"; FLASH_MB=4 ;;
esac

if [ -f "$BOOT" ] && [ -f "$PART" ] && [ -f "$APPBIN" ]; then
  echo "[run] Creando imagen SPI flash ${FLASH_MB}MB en $FLASHIMG"
  dd if=/dev/zero bs=1M count="$FLASH_MB" of="$FLASHIMG" status=none
  dd if="$BOOT" bs=1 count=$(stat -c %s "$BOOT") seek=$((16#1000)) conv=notrunc of="$FLASHIMG" status=none
  dd if="$PART" bs=1 count=$(stat -c %s "$PART") seek=$((16#8000)) conv=notrunc of="$FLASHIMG" status=none
  dd if="$APPBIN" bs=1 count=$(stat -c %s "$APPBIN") seek=$((16#10000)) conv=notrunc of="$FLASHIMG" status=none
  echo "[run] Usando SPI flash emulada: $FLASHIMG"

  # Opciones de memoria y red (NIC open_eth); hostfwd opcional
  QEMU_OPTS+=( -m "$FLASH_MB" -nic user,model=open_eth )
  # Para exponer puertos del guest al host, descomentar y ajustar:
  #QEMU_OPTS+=( -nic user,model=open_eth,hostfwd=tcp::8080-:80 )

  exec qemu-system-xtensa "${QEMU_OPTS[@]}" -drive file="$FLASHIMG",if=mtd,format=raw | python3 tools/bridge.py
else
  echo "[run] Archivos de bootloader/particiones/app no encontrados; usando -kernel ELF"
  exec qemu-system-xtensa "${QEMU_OPTS[@]}" -kernel build/tb_thread_node.elf | python3 tools/bridge.py
fi
