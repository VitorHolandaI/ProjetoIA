from .config import SimulationConfig
from .knowledge import KnowledgeBase
from .maze import Maze
from .models import HumanAgent, MinotaurAgent


def score_human(config: SimulationConfig, maze: Maze, human: HumanAgent) -> float:
    start_distance = maze.shortest_distance(human.entrance, maze.exit_position)
    final_distance = maze.shortest_distance(human.position, maze.exit_position)
    progress_score = max(0, start_distance - final_distance) * 12.0
    escape_score = 900.0 + (config.max_steps - human.steps_alive) * 4.0 if human.escaped else 0.0
    survival_penalty = 300.0 if human.caught else 40.0 if human.timed_out else 0.0
    return max(1.0, progress_score + escape_score - survival_penalty - loop_penalty(human))


def score_minotaurs(
    config: SimulationConfig,
    maze: Maze,
    knowledge: KnowledgeBase,
    minotaurs: list[MinotaurAgent],
    humans: list[HumanAgent],
) -> float:
    captures = sum(len(minotaur.capture_steps) for minotaur in minotaurs)
    escaped = sum(1 for human in humans if human.escaped)
    early_bonus = sum(
        config.max_steps - step
        for minotaur in minotaurs
        for step in minotaur.capture_steps
    )
    patrol_score = sum(
        knowledge.traffic_score(position)
        for minotaur in minotaurs
        for position in minotaur.path
    )
    repeat_penalty = sum(
        max(0, visits - 1)
        for minotaur in minotaurs
        for visits in minotaur.visited_counts.values()
    )
    return max(
        1.0,
        captures * 420.0
        + early_bonus * 2.0
        + patrol_score
        + minotaur_exploration_score(maze, minotaurs)
        - escaped * 20.0
        - repeat_penalty * 1.5,
    )


def minotaur_exploration_score(maze: Maze, minotaurs: list[MinotaurAgent]) -> float:
    score = 0.0
    for minotaur in minotaurs:
        unique_positions = set(minotaur.path)
        farthest_distance = max(
            maze.shortest_distance(maze.minotaur_start, position)
            for position in unique_positions
        )
        score += len(unique_positions) * 12.0
        score += len(minotaur.path) * 0.8
        score += farthest_distance * 10.0
    return score


def loop_penalty(human: HumanAgent) -> float:
    repeat_steps = sum(max(0, visits - 1) for visits in human.visited_counts.values())
    return repeat_steps * 3.0

