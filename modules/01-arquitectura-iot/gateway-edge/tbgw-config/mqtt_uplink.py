from thingsboard_gateway.connectors.mqtt.mqtt_uplink_converter import MqttUplinkConverter

class CustomMqttUplinkConverter(MqttUplinkConverter):
    def convert(self, config, topic, data):
        # Simple example: device name from last topic level
        device = topic.split('/')[-1]
        return {
            'deviceName': device,
            'telemetry': [{k: v} for k, v in (data if isinstance(data, dict) else {}).items()]
        }
