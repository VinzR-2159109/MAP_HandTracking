from mqtt_handler import MQTTHandler
from hand_tracker import HandTracker
from video_streamer import VideoStreamer
import cv2

if __name__ == "__main__":
    # Initialize MQTT Handler
    mqtt_handler = MQTTHandler(
        broker="0f158df0574242429e54c7458f9f4a37.s1.eu.hivemq.cloud",
        port=8883,
        username="dwi_map",
        password="wRYx&RK%l5vsflnN",
        sub_topic="sensor/commands"
    )

    # Initialize Hand Tracker
    tracker = HandTracker(source=4)

    # Start Video Streamer (Configurable Host & Port)
    video_streamer = VideoStreamer(host="0.0.0.0", port=5000)
    video_streamer.start()

    while True:
        frame, hand_positions = tracker.get_frame()
        if frame is None:
            break
        
        # Debug:
        cv2.imshow("Hand Tracking", frame)

        video_streamer.update_frame(frame)

        if hand_positions and tracker.has_position_changed(hand_positions):
            data_to_send = hand_positions.to_json()
            mqtt_handler.publish(data_to_send, topic="sensor/hands/position")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    del tracker
