import json
import os
import time
import threading
from typing import Dict, Any, Set

import paho.mqtt.client as mqtt
from tb_gateway_mqtt import TBGatewayMqttClient

# ThingsBoard connection
TB_HOST = os.getenv("TB_HOST", "localhost")
TB_PORT = int(os.getenv("TB_PORT", "1883"))
TB_TOKEN = os.getenv("TB_TOKEN", "9YQfeQcVaKRTUm6EVz6S")

# Children seed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHILDREN_FILE = os.getenv("GW_CHILDREN_FILE", os.path.join(os.path.dirname(BASE_DIR), "devices.json"))


def load_children() -> Dict[str, Dict[str, float]]:
    try:
        if os.path.exists(DEFAULT_CHILDREN_FILE):
            with open(DEFAULT_CHILDREN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {k: dict(v) for k, v in data.items()}
    except Exception as e:
        print(f"[WARN] No se pudo leer {DEFAULT_CHILDREN_FILE}: {e}")
    env_children = os.getenv("GW_CHILDREN")
    if env_children:
        names = [x.strip() for x in env_children.split(",") if x.strip()]
        return {name: {"temperature": 24.0, "humidity": 60.0} for name in names}
    return {"node-1": {"temperature": 24.3, "humidity": 60.1}, "node-2": {"temperature": 25.0, "humidity": 58.7}}


SENSORS: Dict[str, Dict[str, float]] = load_children()
GW_SIMULATE_CHILDREN = os.getenv("GW_SIMULATE_CHILDREN", "false").lower() == "true"

# Local connector config
CONNECTOR_MQTT_ENABLE = os.getenv("CONNECTOR_MQTT_ENABLE", "true").lower() == "true"
CONNECTOR_MQTT_HOST = os.getenv("CONNECTOR_MQTT_HOST", "mosquitto")
CONNECTOR_MQTT_PORT = int(os.getenv("CONNECTOR_MQTT_PORT", "1883"))
CONNECTOR_TOPIC_PREFIX = os.getenv("CONNECTOR_TOPIC_PREFIX", "devices")
CONNECTOR_TOPIC_PREFIX_ALT = os.getenv("CONNECTOR_TOPIC_PREFIX_ALT", "sensor")

CONNECTED_CHILDREN: Set[str] = set()


def ensure_child_connected(tb: TBGatewayMqttClient, device: str):
    if not device or str(device).strip() == "":
        print("[WARN] Ignorando solicitud de conexión: nombre de dispositivo vacío")
        return
    if device in CONNECTED_CHILDREN:
        return
    try:
        tb.gw_connect_device(device)
        tb.gw_send_attributes(device, {"role": "simulated", "group": "lab"})
        CONNECTED_CHILDREN.add(device)
        print(f"[TB] Child connected: {device}")
    except Exception as e:
        print(f"[WARN] connect/send attrs failed for {device}: {e}")


def publish_telemetry_loop(tb: TBGatewayMqttClient):
    period = int(os.getenv("GW_PERIOD_SEC", "5"))
    while True:
        ts = int(time.time() * 1000)
        for dev, vals in SENSORS.items():
            vals["temperature"] = float(vals.get("temperature", 0.0)) + 0.01
            vals["humidity"] = float(vals.get("humidity", 0.0)) + 0.01
            try:
                tb.gw_send_telemetry(dev, {"ts": ts, "values": dict(vals)})
            except Exception as e:
                print("[WARN] gw_send_telemetry failed:", e)
        time.sleep(period)


def start_connector(tb: TBGatewayMqttClient) -> mqtt.Client | None:
    if not CONNECTOR_MQTT_ENABLE:
        return None
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                         client_id=f"edge-connector-{int(time.time())}")

    def _on_connect(c, u, flags, reasonCode, properties):
        try:
            rc_val = int(getattr(reasonCode, "value", reasonCode))
        except Exception:
            rc_val = str(reasonCode)
        print(f"[Connector] Connected to MQTT broker {CONNECTOR_MQTT_HOST}:{CONNECTOR_MQTT_PORT} rc={rc_val}")
        base = CONNECTOR_TOPIC_PREFIX
        base2 = CONNECTOR_TOPIC_PREFIX_ALT
        c.subscribe([
            (f"{base}/+/telemetry", 0),
            (f"{base}/+/attributes", 0),
            (f"{base}/+/rpc/response/+", 0),
            (f"{base2}/data", 0),
            (f"{base2}/+/data", 0),
            (f"{base2}/raw_data", 0),
            (f"custom/sensors/+", 0),
            (f"{base2}/connect", 0),
            (f"{base2}/+/connect", 0),
            (f"{base2}/disconnect", 0),
            (f"{base2}/+/disconnect", 0),
            ("data/#", 0),
        ])

    def _tb_send_telemetry(device: str, values: Dict[str, Any], ts: int | None = None):
        if not device or str(device).strip() == "":
            print("[Connector][WARN] Telemetría descartada: nombre de dispositivo vacío")
            return
        ensure_child_connected(tb, device)
        pkt = {"values": values}
        if ts is not None:
            pkt["ts"] = ts
        try:
            tb.gw_send_telemetry(device, pkt)
            # log compacto
            sample = ", ".join(f"{k}={v}" for k, v in list(values.items())[:3]) if isinstance(values, dict) else str(values)
            print(f"[Connector] >> TB telemetry {device}: {sample}")
        except Exception as e:
            print("[Connector][WARN] telemetry send failed:", e)

    def _on_message(c, u, msg: mqtt.MQTTMessage):
        try:
            topic = msg.topic
            parts = topic.split("/")
            base = CONNECTOR_TOPIC_PREFIX
            base2 = CONNECTOR_TOPIC_PREFIX_ALT
            try:
                payload = json.loads(msg.payload.decode("utf-8")) if msg.payload else {}
            except Exception:
                payload = msg.payload

            # devices/* schema
            if len(parts) >= 3 and parts[0] == base:
                device, action = parts[1], parts[2]
                if action == "telemetry":
                    ts = int(time.time() * 1000)
                    if isinstance(payload, dict) and ("values" in payload or "ts" in payload):
                        values = payload.get("values", {})
                        ts = int(payload.get("ts", ts))
                    else:
                        values = payload if isinstance(payload, dict) else {"raw": str(payload)}
                    _tb_send_telemetry(device, values, ts)
                    return
                if action == "attributes":
                    ensure_child_connected(tb, device)
                    if isinstance(payload, dict):
                        tb.gw_send_attributes(device, payload)
                    else:
                        tb.gw_send_attributes(device, {"raw": str(payload)})
                    return
                if action == "rpc" and len(parts) >= 5 and parts[3] == "response":
                    req_id = parts[4]
                    try:
                        tb.gw_send_rpc_reply(device, req_id, payload if isinstance(payload, dict) else {"result": payload})
                    except Exception as e:
                        print("[Connector][WARN] rpc reply failed:", e)
                    return

            # sensor/* schema
            if parts[0] == base2:
                if parts[1] == "data" and len(parts) == 2:
                    if isinstance(payload, dict) and "device" in payload:
                        dev = str(payload.get("device"))
                        values = payload.get("values") or {k: v for k, v in payload.items() if k != "device"}
                        _tb_send_telemetry(dev, values)
                    return
                if len(parts) >= 3 and parts[2] == "data":
                    dev = parts[1]
                    values = payload if isinstance(payload, dict) else {"raw": str(payload)}
                    _tb_send_telemetry(dev, values)
                    return
                if parts[1] == "raw_data":
                    dev = "raw-sensor"
                    values = {"raw": msg.payload.hex() if isinstance(payload, (bytes, bytearray)) else str(payload)}
                    _tb_send_telemetry(dev, values)
                    return
                if parts[1] == "connect" or (len(parts) >= 3 and parts[2] == "connect"):
                    dev = payload.get("device") if isinstance(payload, dict) and "device" in payload else (parts[1] if len(parts) >= 2 else None)
                    if dev:
                        ensure_child_connected(tb, dev)
                    return
                if parts[1] == "disconnect" or (len(parts) >= 3 and parts[2] == "disconnect"):
                    dev = payload.get("device") if isinstance(payload, dict) and "device" in payload else (parts[1] if len(parts) >= 2 else None)
                    if dev and dev in CONNECTED_CHILDREN:
                        CONNECTED_CHILDREN.discard(dev)
                        try:
                            tb.gw_disconnect_device(dev)
                        except Exception:
                            pass
                    return

            # generic data/#
            if parts[0] == "data":
                # admitir 'data' y 'data/' como raíz
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                    if isinstance(payload, dict) and "device" in payload:
                        dev = str(payload.get("device"))
                        values = payload.get("values") or {k: v for k, v in payload.items() if k != "device"}
                        _tb_send_telemetry(dev, values)
                    else:
                        print("[Connector][WARN] 'data' o 'data/' sin campo 'device' en el payload")
                    return
                else:
                    dev = parts[1]
                    values = payload if isinstance(payload, dict) else {"raw": str(payload)}
                    _tb_send_telemetry(dev, values)
                    return
        except Exception as e:
            print("[Connector][WARN] Error processing message:", e)

    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(CONNECTOR_MQTT_HOST, CONNECTOR_MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


def main():
    if TB_TOKEN == "YOUR_GATEWAY_TOKEN":
        print("[ERROR] Debes configurar TB_TOKEN con el token del dispositivo Gateway en ThingsBoard.")
        return
    tb = TBGatewayMqttClient(TB_HOST, TB_PORT, TB_TOKEN)
    tb.connect()
    # Esperar conexión real antes de enviar datos
    start = time.time()
    timeout = int(os.getenv("TB_CONNECT_TIMEOUT_SEC", "15"))
    while True:
        try:
            if hasattr(tb, "is_connected") and tb.is_connected():
                print(f"[TB] Connected to {TB_HOST}:{TB_PORT} (gateway token)")
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            print(f"[ERROR] No se estableció conexión con TB en {timeout}s ({TB_HOST}:{TB_PORT}).")
            # Continuamos pero evitamos enviar inmediatamente
            break
        time.sleep(0.2)
    # Connect children seed (si ya hay conexión)
    if hasattr(tb, "is_connected") and tb.is_connected():
        for dev in SENSORS.keys():
            ensure_child_connected(tb, dev)
    # Start connector bridge
    start_connector(tb)
    # Optional simulated telemetry
    if GW_SIMULATE_CHILDREN:
        threading.Thread(target=publish_telemetry_loop, args=(tb,), daemon=True).start()
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
