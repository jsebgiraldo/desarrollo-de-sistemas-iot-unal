#!/usr/bin/env python3
import os
import time
import json
import random
import paho.mqtt.client as mqtt

TB_HOST = os.getenv("TB_HOST", "localhost")
TB_PORT = int(os.getenv("TB_PORT", "1883"))
TB_TOKEN = os.getenv("TB_TOKEN", "YOUR_TB_DEVICE_TOKEN")

client = mqtt.Client()
client.username_pw_set(TB_TOKEN)
client.connect(TB_HOST, TB_PORT, 60)
print(f"[sim] Connected to MQTT {TB_HOST}:{TB_PORT}")

try:
    while True:
        payload = {
            "temperature": round(24 + random.random(), 2),
            "humidity": round(60 + random.random(), 2)
        }
        s = json.dumps(payload)
        client.publish("v1/devices/me/telemetry", s)
        print(f"[sim] published {s}")
        time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()
