# Stage 1: build QEMU (builder-only)
FROM espressif/idf:latest AS qemu-builder

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git build-essential ninja-build meson pkg-config \
       libglib2.0-dev libpixman-1-dev zlib1g-dev \
       libgcrypt20-dev libgpg-error-dev libslirp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/espressif
RUN git clone --depth 1 https://github.com/espressif/qemu.git qemu \
 && cd qemu \
 && ./configure --target-list=xtensa-softmmu --prefix=/opt/espressif/qemu-install \
 && make -j"$(nproc)" \
 && make install \
 && test -x /opt/espressif/qemu-install/bin/qemu-system-xtensa

# Stage 2: final runtime image (smaller)
FROM espressif/idf:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-venv python3-paho-mqtt \
       libglib2.0-0 libpixman-1-0 zlib1g \
       libgcrypt20 libgpg-error0 libslirp0 \
    && rm -rf /var/lib/apt/lists/*

# Auto-source ESP-IDF env for interactive shells
RUN echo 'if [ -f /opt/esp/idf/export.sh ]; then . /opt/esp/idf/export.sh >/dev/null 2>&1; fi' >> /etc/bash.bashrc \
 && printf '#!/bin/sh\n[ -f /opt/esp/idf/export.sh ] && . /opt/esp/idf/export.sh\n' > /etc/profile.d/esp-idf.sh \
 && chmod +x /etc/profile.d/esp-idf.sh

WORKDIR /workspace

# Crear venv y preinstalar herramientas
RUN python3 -m venv /opt/pytools \
 && /opt/pytools/bin/pip install --upgrade pip setuptools wheel

# Instalar requerimientos de Python del proyecto (bridge/simulator)
COPY tools/requirements.txt /tmp/pytools-requirements.txt
RUN /opt/pytools/bin/pip install --no-cache-dir -r /tmp/pytools-requirements.txt

# Copiar QEMU construido desde el builder
COPY --from=qemu-builder /opt/espressif/qemu-install /opt/espressif/qemu-install

# Priorizar el QEMU de Espressif en PATH y el venv de pytools
ENV PATH="/opt/espressif/qemu-install/bin:/opt/pytools/bin:${PATH}"

# Default command
CMD ["bash"]
