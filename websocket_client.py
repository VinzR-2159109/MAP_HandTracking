
import threading
from websocket import create_connection, WebSocketConnectionClosedException

class WebSocketClient:
    def __init__(self):
        self.ws = None
        self.url = None
        self.lock = threading.Lock()

    def connect(self, url):
        with self.lock:
            try:
                if self.ws:
                    self.ws.close()
                self.ws = create_connection(url)
                self.url = url
                print(f"✅ WebSocket connected to {url}")
            except Exception as e:
                print(f"❌ WebSocket connection failed: {e}")
                self.ws = None

    def send(self, message):
        with self.lock:
            if self.ws:
                try:
                    self.ws.send(message)
                except WebSocketConnectionClosedException:
                    print("⚠️ WebSocket connection closed")
                    self.ws = None
                except Exception as e:
                    print(f"❌ WebSocket send error: {e}")

    def is_connected(self):
        return self.ws is not None
