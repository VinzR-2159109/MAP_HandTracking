from dataclasses import dataclass
from DataClasses.Position import Position

@dataclass
class Hand:
    """Represents a detected hand with label, position, and tracking status."""
    label: str
    position: Position
    status: str  # 'detected' or 'unknown'

    def to_dict(self):
        return {
            "hand": self.label,
            "position": self.position.to_dict(),
            "status": self.status
        }
