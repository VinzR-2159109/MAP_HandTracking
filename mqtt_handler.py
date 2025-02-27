import paho.mqtt.client as mqtt
import json
import threading

class MQTTHandler:
    """Handles MQTT connection"""
    def __init__(self, broker, port, username, password, sub_topic):
        
        self.client = mqtt.Client()

        self.client.tls_set()
        self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.broker = broker
        self.port = port
        self.sub_topic = sub_topic
        self.connected = False

        try:
            self.client.connect(broker, port, keepalive=60)
            self.connected = True
        except Exception as e:
            print(f"MQTT Connection Error: {e}")
            self.connected = False

        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self.thread.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Connected to MQTT broker.")
            self.client.subscribe(self.sub_topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker.")
        self.connected = False

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            print(f"Debug: Received message on {message.topic}: {payload}")
        except json.JSONDecodeError:
            print(f"Invalid JSON message received: {message.payload}")

    def publish(self, message, topic="sensor/hands/position"):
        if self.connected:
            try:
                self.client.publish(topic, message)  # No need to use json.dumps again
                print(f"Published to {topic}: {message}")
            except Exception as e:
                print(f"Error publishing message: {e}")
        else:
            print("MQTT is not connected. Message not sent.")
