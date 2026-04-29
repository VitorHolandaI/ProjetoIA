from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class HumanDNA:
    exploration_rate: float
    exit_bias: float
    landmark_memory_weight: float
    danger_avoidance_weight: float
    loop_penalty_weight: float
    minotaur_fear_weight: float

    @classmethod
    def random(cls, rng: Random) -> "HumanDNA":
        return cls(
            exploration_rate=rng.uniform(0.05, 0.45),
            exit_bias=rng.uniform(0.20, 1.00),
            landmark_memory_weight=rng.uniform(0.00, 1.00),
            danger_avoidance_weight=rng.uniform(0.00, 1.00),
            loop_penalty_weight=rng.uniform(0.20, 1.00),
            minotaur_fear_weight=rng.uniform(0.00, 1.00),
        )

    def crossover(self, partner: "HumanDNA", rng: Random) -> "HumanDNA":
        return HumanDNA(
            exploration_rate=_pick(self.exploration_rate, partner.exploration_rate, rng),
            exit_bias=_pick(self.exit_bias, partner.exit_bias, rng),
            landmark_memory_weight=_pick(
                self.landmark_memory_weight, partner.landmark_memory_weight, rng
            ),
            danger_avoidance_weight=_pick(
                self.danger_avoidance_weight, partner.danger_avoidance_weight, rng
            ),
            loop_penalty_weight=_pick(self.loop_penalty_weight, partner.loop_penalty_weight, rng),
            minotaur_fear_weight=_pick(
                self.minotaur_fear_weight, partner.minotaur_fear_weight, rng
            ),
        )

    def mutate(self, mutation_rate: float, rng: Random) -> "HumanDNA":
        return HumanDNA(
            exploration_rate=_mutate(self.exploration_rate, mutation_rate, rng),
            exit_bias=_mutate(self.exit_bias, mutation_rate, rng),
            landmark_memory_weight=_mutate(self.landmark_memory_weight, mutation_rate, rng),
            danger_avoidance_weight=_mutate(self.danger_avoidance_weight, mutation_rate, rng),
            loop_penalty_weight=_mutate(self.loop_penalty_weight, mutation_rate, rng),
            minotaur_fear_weight=_mutate(self.minotaur_fear_weight, mutation_rate, rng),
        )


@dataclass(frozen=True)
class MinotaurDNA:
    chase_weight: float
    traffic_weight: float
    landmark_patrol_weight: float
    entrance_prediction_weight: float
    random_patrol_rate: float

    @classmethod
    def random(cls, rng: Random) -> "MinotaurDNA":
        return cls(
            chase_weight=rng.uniform(0.20, 1.00),
            traffic_weight=rng.uniform(0.00, 1.00),
            landmark_patrol_weight=rng.uniform(0.00, 1.00),
            entrance_prediction_weight=rng.uniform(0.00, 1.00),
            random_patrol_rate=rng.uniform(0.02, 0.35),
        )

    def crossover(self, partner: "MinotaurDNA", rng: Random) -> "MinotaurDNA":
        return MinotaurDNA(
            chase_weight=_pick(self.chase_weight, partner.chase_weight, rng),
            traffic_weight=_pick(self.traffic_weight, partner.traffic_weight, rng),
            landmark_patrol_weight=_pick(
                self.landmark_patrol_weight, partner.landmark_patrol_weight, rng
            ),
            entrance_prediction_weight=_pick(
                self.entrance_prediction_weight, partner.entrance_prediction_weight, rng
            ),
            random_patrol_rate=_pick(self.random_patrol_rate, partner.random_patrol_rate, rng),
        )

    def mutate(self, mutation_rate: float, rng: Random) -> "MinotaurDNA":
        return MinotaurDNA(
            chase_weight=_mutate(self.chase_weight, mutation_rate, rng),
            traffic_weight=_mutate(self.traffic_weight, mutation_rate, rng),
            landmark_patrol_weight=_mutate(self.landmark_patrol_weight, mutation_rate, rng),
            entrance_prediction_weight=_mutate(
                self.entrance_prediction_weight, mutation_rate, rng
            ),
            random_patrol_rate=_mutate(self.random_patrol_rate, mutation_rate, rng),
        )


def _pick(left: float, right: float, rng: Random) -> float:
    if rng.random() < 0.40:
        return left
    if rng.random() < 0.80:
        return right
    return (left + right) / 2.0


def _mutate(value: float, mutation_rate: float, rng: Random) -> float:
    if rng.random() >= mutation_rate:
        return value
    return _clamp(value + rng.gauss(0.0, 0.16))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

