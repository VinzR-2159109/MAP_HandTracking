from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

    def to_dict(self):
        return {"x": self.x, "y": self.y}
