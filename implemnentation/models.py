from dataclasses import dataclass, field

from .dna import HumanDNA, MinotaurDNA
from .maze import Position


@dataclass
class HumanAgent:
    dna: HumanDNA
    entrance: Position
    position: Position
    path: list[Position] = field(default_factory=list)
    seen_landmarks: set[str] = field(default_factory=set)
    landmark_memory: dict[str, int] = field(default_factory=dict)
    visited_counts: dict[Position, int] = field(default_factory=dict)
    escaped: bool = False
    caught: bool = False
    timed_out: bool = False
    steps_alive: int = 0

    @classmethod
    def spawn(cls, dna: HumanDNA, entrance: Position) -> "HumanAgent":
        return cls(dna=dna, entrance=entrance, position=entrance, path=[entrance])

    @property
    def is_alive(self) -> bool:
        return not self.escaped and not self.caught and not self.timed_out


@dataclass
class MinotaurAgent:
    dna: MinotaurDNA
    position: Position
    path: list[Position] = field(default_factory=list)
    visited_counts: dict[Position, int] = field(default_factory=dict)
    capture_steps: list[int] = field(default_factory=list)

    @classmethod
    def spawn(cls, dna: MinotaurDNA, position: Position) -> "MinotaurAgent":
        return cls(dna=dna, position=position, path=[position])


@dataclass(frozen=True)
class HumanRunEvent:
    entrance: Position
    path: list[Position]
    seen_landmarks: set[str]
    outcome: str


@dataclass(frozen=True)
class TrialResult:
    human_scores: list[float]
    human_escaped_flags: list[bool]
    human_events: list[HumanRunEvent]
    minotaur_score: float
    escaped_count: int
    caught_count: int
    timed_out_count: int
    best_path: list[Position] | None


@dataclass(frozen=True)
class GenerationStats:
    generation: int
    best_human_fitness: float
    average_human_fitness: float
    best_minotaur_fitness: float
    average_minotaur_fitness: float
    average_escaped: float
    average_caught: float
    average_timed_out: float
    best_path_length: int | None
    best_minotaur_path_length: int | None
    best_minotaur_unique_cells: int | None
