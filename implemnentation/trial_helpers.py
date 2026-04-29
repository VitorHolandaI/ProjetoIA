from .maze import Position
from .models import HumanAgent


def add_scores(left: list[float], right: list[float]) -> list[float]:
    return [left_score + right_score for left_score, right_score in zip(left, right, strict=True)]


def or_flags(left: list[bool], right: list[bool]) -> list[bool]:
    return [left_flag or right_flag for left_flag, right_flag in zip(left, right, strict=True)]


def best_escaped_path(humans: list[HumanAgent]) -> list[Position] | None:
    escaped_paths = [human.path for human in humans if human.escaped]
    if not escaped_paths:
        return None
    return min(escaped_paths, key=len)

