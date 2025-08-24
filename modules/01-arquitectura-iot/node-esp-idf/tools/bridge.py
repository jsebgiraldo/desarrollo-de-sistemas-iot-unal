#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import paho.mqtt.client as mqtt

ENV_HOST = os.getenv("TB_HOST", os.getenv("TB_FALLBACK_HOST", "")).strip()
TB_PORT = int(os.getenv("TB_PORT", "1883"))
TB_TOKEN = os.getenv("TB_TOKEN", "YOUR_TB_DEVICE_TOKEN")

def resolve_host():
    candidates = []
    if ENV_HOST:
        candidates.append(ENV_HOST)
    candidates += ["tb", "tb-ce", "host.docker.internal", "localhost"]
    for h in candidates:
        try:
            socket.getaddrinfo(h, TB_PORT, proto=socket.IPPROTO_TCP)
            print(f"[bridge] Using host: {h}")
            return h
        except Exception:
            continue
    raise RuntimeError("No MQTT host resolved. Set TB_HOST env var.")

TB_HOST = resolve_host()

client = mqtt.Client()
client.username_pw_set(TB_TOKEN)

def connect_with_retry():
    while True:
        try:
            client.connect(TB_HOST, TB_PORT, 60)
            print(f"[bridge] Connected to MQTT {TB_HOST}:{TB_PORT} as token")
            return
        except Exception as e:
            print(f"[bridge] connect failed to {TB_HOST}:{TB_PORT}: {e}")
            time.sleep(2)

def main():
    connect_with_retry()
    client.loop_start()
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            if line.startswith("TBTELEMETRY:"):
                payload = line.split("TBTELEMETRY:",1)[1].strip()
                try:
                    json.loads(payload)  # validate
                except json.JSONDecodeError:
                    print(f"[bridge] invalid JSON: {payload}")
                    continue
                try:
                    client.publish("v1/devices/me/telemetry", payload)
                    print(f"[bridge] published {payload}")
                except Exception as e:
                    print(f"[bridge] publish failed: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
