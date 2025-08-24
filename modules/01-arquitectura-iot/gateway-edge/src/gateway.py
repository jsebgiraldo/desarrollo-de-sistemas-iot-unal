import json
import os
import time
import threading
from typing import Dict

import paho.mqtt.client as mqtt

TB_HOST = os.getenv("TB_HOST", "localhost")
TB_PORT = int(os.getenv("TB_PORT", "1883"))
TB_TOKEN = os.getenv("TB_TOKEN", "YOUR_GATEWAY_TOKEN")

CLIENT_ID = f"edge-gw-{int(time.time())}"

# Simulación de 2 nodos hijos
SENSORS: Dict[str, Dict[str, float]] = {
    "node-1": {"temperature": 24.3, "humidity": 60.1},
    "node-2": {"temperature": 25.0, "humidity": 58.7},
}


def on_connect(client, userdata, flags, rc):
    print("Connected to TB MQTT with rc=", rc)
    # Conectar dispositivos hijos (API de gateway)
    for dev in SENSORS.keys():
        client.publish("v1/gateway/connect", json.dumps({"device": dev}))
        print(f"Connected child device: {dev}")


def publish_telemetry_loop(client: mqtt.Client):
    while True:
        ts = int(time.time() * 1000)
        payload: Dict[str, list] = {}
        # Agregación simple de nodos hijos
        for dev, vals in SENSORS.items():
            vals["temperature"] += 0.01
            vals["humidity"] += 0.01
            payload[dev] = [{"ts": ts, "values": dict(vals)}]
        # Topic gateway API correcto
        topic = "v1/gateway/telemetry"
        client.publish(topic, json.dumps(payload))
        print("Published:", payload)
        time.sleep(5)


def main():
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
    client.username_pw_set(TB_TOKEN)
    client.on_connect = on_connect
    client.connect(TB_HOST, TB_PORT, keepalive=60)

    t = threading.Thread(target=publish_telemetry_loop, args=(client,), daemon=True)
    t.start()

    client.loop_forever()


if __name__ == "__main__":
    main()
