from collections.abc import Callable, Sequence
from random import Random
from typing import TypeVar

T = TypeVar("T")


def make_next_generation(
    scored_population: Sequence[tuple[T, float]],
    size: int,
    elite_count: int,
    mutation_rate: float,
    rng: Random,
    crossover: Callable[[T, T, Random], T],
    mutate: Callable[[T, float, Random], T],
) -> list[T]:
    sorted_population = sorted(scored_population, key=lambda item: item[1], reverse=True)
    next_generation = [individual for individual, _ in sorted_population[:elite_count]]
    while len(next_generation) < size:
        parent_a = select_parent(sorted_population, rng)
        parent_b = select_parent(sorted_population, rng)
        child = crossover(parent_a, parent_b, rng)
        next_generation.append(mutate(child, mutation_rate, rng))
    return next_generation


def select_parent(scored_population: Sequence[tuple[T, float]], rng: Random) -> T:
    minimum = min(score for _, score in scored_population)
    offset = abs(minimum) + 1.0 if minimum <= 0.0 else 0.0
    total = sum(score + offset for _, score in scored_population)
    if total <= 0.0:
        return rng.choice([individual for individual, _ in scored_population])
    pick = rng.uniform(0.0, total)
    current = 0.0
    for individual, score in scored_population:
        current += score + offset
        if current >= pick:
            return individual
    return scored_population[-1][0]

