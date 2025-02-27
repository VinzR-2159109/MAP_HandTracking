from flask import Flask, Response
import threading
import cv2

class VideoStreamer:
    def __init__(self, host="0.0.0.0", port=5000):
        """Initialize the Video Streamer with a configurable host and port."""
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.latest_frame = None

        @self.app.route('/video_feed')
        def video_feed():
            """HTTP endpoint for video streaming."""
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def update_frame(self, frame):
        """Update the latest frame from an external source (HandTracker)."""
        self.latest_frame = frame

    def generate_frames(self):
        """Continuously yield the latest frame as an MJPEG stream."""
        while True:
            if self.latest_frame is not None:
                _, buffer = cv2.imencode(".jpeg", self.latest_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def start(self):
        """Start the Flask server in a separate thread."""
        flask_thread = threading.Thread(
            target=self.app.run, 
            kwargs={'host': self.host, 'port': self.port, 'debug': False, 'use_reloader': False}
        )
        flask_thread.daemon = True
        flask_thread.start()
