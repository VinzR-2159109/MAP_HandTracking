# https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

from mqtt_handler import MQTTHandler
from hand_tracker import HandTracker
from video_streamer import VideoStreamer
from websocket_client import WebSocketClient
import cv2

def on_mqtt_message(topic, msg):
    global ws_client
    try:
        if (topic  == "Command/HandTracking"):
            if msg.get("key") == "websocket" and msg.get("action") == "connect":
                url = msg.get("data")
                ws_client.connect(url)
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

if __name__ == "__main__":
    mqtt_handler = MQTTHandler(
        broker="0f158df0574242429e54c7458f9f4a37.s1.eu.hivemq.cloud",
        port=8883,
        username="dwi_map",
        password="wRYx&RK%l5vsflnN",
        sub_topic="sensor/commands",
        message_callback=on_mqtt_message
    )

    ws_client = WebSocketClient()
    
    tracker = HandTracker(source=4)
    video_streamer = VideoStreamer(host="0.0.0.0", port=5000)
    video_streamer.start()

    mqtt_handler.subscribe("Command/HandTracking")

    try:
        while True:
            frame, hand_positions = tracker.get_frame()
            if frame is None:
                break

            cv2.imshow("Hand Tracking", frame)
            video_streamer.update_frame(frame)

            if hand_positions and tracker.has_position_changed(hand_positions):
                data = hand_positions.to_json()
                if ws_client.is_connected():
                    ws_client.send(data)
                else:
                    print("📭 No WebSocket connection")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("🛑 Stopping due to keyboard interrupt...")

    finally:
        cv2.destroyAllWindows()
        del tracker
