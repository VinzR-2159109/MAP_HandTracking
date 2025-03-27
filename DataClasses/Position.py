from dataclasses import dataclass
from typing import Optional

@dataclass
class Position:
    x: int
    y: int
    index: Optional[int] = None

    def to_dict(self):
        data = {"x": int(self.x), "y": int(self.y)}
        if self.index is not None:
            data["index"] = self.index
        return data
