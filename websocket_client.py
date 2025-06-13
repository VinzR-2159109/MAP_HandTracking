import threading
import time
from websocket import create_connection, WebSocketConnectionClosedException

class WebSocketClient:
    def __init__(self):
        self.ws = None
        self.url = None
        self.lock = threading.Lock()
        self.urls = []
        self.should_reconnect = True

    def connect(self, url):
        with self.lock:
            try:
                if self.ws:
                    self.ws.close()
                self.ws = create_connection(url)
                self.url = url
                if url not in self.urls:
                    self.urls.append(url)
                print(f"✅ WebSocket connected to {url}")
            except Exception as e:
                print(f"❌ WebSocket connection failed: {e}")
                self.ws = None

        if self.should_reconnect:
            threading.Thread(target=self._reconnect_loop, daemon=True).start()

    def send(self, message):
        with self.lock:
            if self.ws:
                try:
                    self.ws.send(message)
                except (WebSocketConnectionClosedException, OSError) as e:
                    print(f"❌ WebSocket send error: {e}")
                    self.ws = None
            else:
                print("⚠️ WebSocket is not connected. Message not sent.")

    def is_connected(self):
        return self.ws is not None

    def _reconnect_loop(self):
        while self.should_reconnect:
            with self.lock:
                if self.ws is not None:
                    continue

            for url in self.urls:
                with self.lock:
                    try:
                        self.ws = create_connection(url)
                        self.url = url
                        print(f"🔁 Reconnected to WebSocket: {url}")
                        break
                    except Exception as e:
                        print(f"❌ Reconnect attempt to {url} failed: {e}")
                        self.ws = None
                time.sleep(2)
