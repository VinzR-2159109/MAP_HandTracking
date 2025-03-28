import paho.mqtt.client as mqtt
import json
import threading
import time

class MQTTHandler:
    """Handles MQTT connection"""
    def __init__(self, broker, port, username, password, sub_topic):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.sub_topic = sub_topic
        self.connected = False
        self.should_reconnect = True

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self._connect()

        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)

        except Exception as e:
            print(f"MQTT Initial Connection Error: {e}")
            self.connected = False

    def _start_loop(self):
        while True:
            self.client.loop(timeout=1.0)
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Connected to MQTT broker.")
            self.client.subscribe(self.sub_topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("Disconnected from MQTT broker.")

        if self.should_reconnect:
            print("Attempting to reconnect...")
            while not self.connected:
                try:
                    self.client.reconnect()
                except Exception as e:
                    print(f"Reconnection failed: {e}")
                    time.sleep(2)

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            print(f"Debug: Received message on {message.topic}: {payload}")
        except json.JSONDecodeError:
            print(f"Invalid JSON message received: {message.payload}")

    def publish(self, message, topic="sensor/hands/position"):
        if self.connected:
            try:
                self.client.publish(topic, message)
                print(f"Published to {topic}: {message}")
            except Exception as e:
                print(f"Error publishing message: {e}")
        else:
            print("MQTT is not connected. Message not sent.")
