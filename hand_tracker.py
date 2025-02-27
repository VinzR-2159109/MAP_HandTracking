import cv2
import mediapipe as mp
import numpy as np
import json
import time
from typing import List, Tuple, Optional
from DataClasses.Hand import Hand
from DataClasses.Hands import Hands
from DataClasses.Position import Position

class HandTracker:
    def __init__(self, source=0, max_num_hands=2, unknown_timeout=1.0):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=max_num_hands
        )

        self.cap = cv2.VideoCapture(source) if isinstance(source, (int, str)) else None

        self.last_detected_time = {"Left": time.time(), "Right": time.time()}
        self.unknown_timeout = unknown_timeout
        self.sent_unknown = {"Left": False, "Right": False}
        self.last_sent_data = None

    def process_frame(self, frame) -> Tuple[np.ndarray, Hands]:
        """Process a frame: detect hands, draw landmarks, and return a Hands object."""
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        detected_hands = {"Left": None, "Right": None}

        if result.multi_hand_landmarks and result.multi_handedness:
            for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
                hand_label = result.multi_handedness[idx].classification[0].label

                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                h, w, _ = frame.shape
                coords = np.array([(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark])
                avg_x, avg_y = map(int, np.mean(coords, axis=0))

                detected_hands[hand_label] = Hand(
                    label=hand_label, position=Position(x=avg_x, y=avg_y), status="detected"
                )

                cv2.circle(frame, (avg_x, avg_y), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"{hand_label} ({avg_x},{avg_y})", (avg_x, avg_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                print(f"Debug: {hand_label} ({avg_x},{avg_y})")

                self.last_detected_time[hand_label] = time.time()
                self.sent_unknown[hand_label] = False

        for hand in ["Left", "Right"]:
            if detected_hands[hand] is None:
                if not self.sent_unknown[hand] and (time.time() - self.last_detected_time[hand] > self.unknown_timeout):
                    detected_hands[hand] = Hand(label=hand, position=Position(x=-1, y=-1), status="unknown")
                    self.sent_unknown[hand] = True

        hands_list = [
            detected_hands["Left"] if detected_hands["Left"] else Hand(label="Left", position=Position(x=-1, y=-1), status="unknown"),
            detected_hands["Right"] if detected_hands["Right"] else Hand(label="Right", position=Position(x=-1, y=-1), status="unknown"),
        ]

        return frame, Hands(detected_hands=hands_list)

    def get_frame(self) -> Tuple[Optional[np.ndarray], Optional[Hands]]:
        """Capture and process a frame from the video source."""
        if self.cap is None or not self.cap.isOpened():
            return None, None

        ret, frame = self.cap.read()
        return self.process_frame(frame) if ret else (None, None)

    def has_position_changed(self, new_hands: Hands) -> bool:
        """Check if hand positions have changed since last sent data."""
        new_data = new_hands.to_json()

        if self.last_sent_data != new_data:
            self.last_sent_data = new_data
            return True

        return False

    def __del__(self):
        """Release resources when the object is destroyed."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
