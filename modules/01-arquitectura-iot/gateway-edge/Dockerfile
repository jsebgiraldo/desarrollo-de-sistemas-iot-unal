# syntax=docker/dockerfile:1
FROM python:3.12-slim

# System deps (optional: tini for signal handling)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and default devices
COPY src/ ./src/
COPY devices.json ./devices.json

# Runtime env
ENV PYTHONUNBUFFERED=1 \
    TB_HOST=tb \
    TB_PORT=1883 \
    TB_TOKEN=YOUR_GATEWAY_TOKEN \
    GW_CHILDREN_FILE=/app/devices.json \
    GW_PERIOD_SEC=5

# Use tini as entrypoint for signal forwarding
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-u", "src/gateway.py"]
