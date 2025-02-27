from dataclasses import dataclass
from typing import List
from DataClasses.Hand import Hand
import json

@dataclass
class Hands:
    """Represents multiple detected hands."""
    detected_hands: List[Hand]

    def to_json(self) -> str:
        """Convert hands data to JSON format."""
        return json.dumps([hand.to_dict() for hand in self.detected_hands])

    def to_dict(self):
        """Convert hand data to a dictionary."""
        return {"hands": [hand.to_dict() for hand in self.detected_hands]}
