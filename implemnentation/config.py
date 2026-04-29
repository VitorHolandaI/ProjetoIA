from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    generations: int = 40
    human_population: int = 30
    minotaur_population: int = 8
    active_minotaurs: int = 2
    max_steps: int = 180
    mutation_rate: float = 0.08
    elite_count: int = 2
    random_seed: int | None = 13
    human_sight: int = 4
    human_hearing: int = 6
    minotaur_sight: int = 7
    minotaur_hearing: int = 10
    minotaur_moves_per_turn: int = 2
    scent_drop_strength: float = 1.0
    scent_decay_rate: float = 0.88
    scent_minimum_strength: float = 0.05
