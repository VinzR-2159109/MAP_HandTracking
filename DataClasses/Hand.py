from dataclasses import dataclass
from DataClasses.Position import Position
from typing import List

@dataclass
class Hand:
    def __init__(self, label: str, position: Position, status: str, landmarks: List[Position]):
        self.label = label
        self.position = position
        self.status = status
        self.landmarks = landmarks

    def to_dict(self):
        return {
            "label": self.label,
            "position": self.position.to_dict(),
            "status": self.status,
            "landmarks": [lm.to_dict() for lm in self.landmarks]
        }

        
