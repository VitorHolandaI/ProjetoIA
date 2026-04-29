from dataclasses import dataclass, field

from .maze import Position


@dataclass
class ScentMap:
    drop_strength: float
    decay_rate: float
    minimum_strength: float
    strengths: dict[Position, float] = field(default_factory=dict)

    def deposit(self, position: Position) -> None:
        self.strengths[position] = self.strengths.get(position, 0.0) + self.drop_strength

    def strength_at(self, position: Position) -> float:
        return self.strengths.get(position, 0.0)

    def decay(self) -> None:
        next_strengths: dict[Position, float] = {}
        for position, strength in self.strengths.items():
            decayed = strength * self.decay_rate
            if decayed >= self.minimum_strength:
                next_strengths[position] = decayed
        self.strengths = next_strengths

