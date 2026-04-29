import argparse
import csv
from pathlib import Path

from .best_path_viewer import show_best_path_with_pygame
from .config import SimulationConfig
from .maze import MAZE_GRIDS, Maze
from .maze_selector import choose_maze_with_pygame
from .models import GenerationStats
from .simulation import LabyrinthEvolution
from .visualizer import run_pygame_evolution, run_visual_evolution


def main() -> None:
    args = parse_args()
    config = SimulationConfig(
        generations=args.generations,
        human_population=args.humans,
        minotaur_population=args.minotaur_strategies,
        active_minotaurs=args.minotaurs,
        max_steps=resolve_time_limit(args),
        mutation_rate=args.mutation,
        random_seed=args.seed,
        minotaur_moves_per_turn=args.minotaur_speed,
    )
    maze = resolve_maze(args)
    if maze is None:
        return
    evolution = LabyrinthEvolution(config, maze=maze)
    visual_fps = resolve_visual_fps(args)
    if args.train_then_show:
        print_header()
        history = evolution.run(on_generation=print_generation)
        show_best_path_with_pygame(evolution, args.tile_size)
    elif args.pygame:
        history = run_pygame_evolution(evolution, visual_fps, args.tile_size)
    elif args.visual:
        history = run_visual_evolution(evolution, visual_fps, not args.no_color)
    else:
        print_header()
        history = evolution.run(on_generation=print_generation)
    if args.csv is not None:
        write_csv(args.csv, history)
    if args.replay and evolution.best_path is not None:
        print("\nBest escaped path:")
        print(evolution.maze.render_path(evolution.best_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minotaur labyrinth genetic algorithm")
    parser.add_argument("--generations", type=int, default=40)
    parser.add_argument("--humans", type=int, default=30)
    parser.add_argument("--minotaurs", type=int, default=2)
    parser.add_argument("--minotaur-strategies", type=int, default=8)
    parser.add_argument("--maze", type=int, choices=sorted(MAZE_GRIDS), default=None)
    parser.add_argument("--steps", type=int, default=180)
    parser.add_argument("--time-limit", type=int, default=None)
    parser.add_argument("--mutation", type=float, default=0.08)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--minotaur-speed", type=int, default=2)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--visual", action="store_true")
    parser.add_argument("--pygame", action="store_true")
    parser.add_argument("--train-then-show", action="store_true")
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--step-delay", type=float, default=None)
    parser.add_argument("--tile-size", type=int, default=40)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()
    if args.humans < 1:
        parser.error("--humans must be at least 1")
    if args.minotaurs < 1:
        parser.error("--minotaurs must be at least 1")
    if args.minotaur_strategies < 1:
        parser.error("--minotaur-strategies must be at least 1")
    if args.steps < 1:
        parser.error("--steps must be at least 1")
    if args.time_limit is not None and args.time_limit < 1:
        parser.error("--time-limit must be at least 1")
    if args.fps < 0:
        parser.error("--fps cannot be negative")
    if args.step_delay is not None and args.step_delay < 0:
        parser.error("--step-delay cannot be negative")
    return args


def resolve_maze(args: argparse.Namespace) -> Maze | None:
    if args.maze is not None:
        return Maze.by_id(args.maze)
    if args.pygame or args.train_then_show:
        return choose_maze_with_pygame()
    return Maze.default()


def resolve_time_limit(args: argparse.Namespace) -> int:
    if args.time_limit is not None:
        return args.time_limit
    return args.steps


def resolve_visual_fps(args: argparse.Namespace) -> float:
    if args.step_delay is None:
        return args.fps
    if args.step_delay == 0:
        return 0.0
    return 1.0 / args.step_delay


def print_header() -> None:
    print(
        "gen | human best | human avg | minotaur best | minotaur avg | "
        "esc | caught | timeout | best path | mino unique"
    )


def print_generation(stats: GenerationStats) -> None:
    path_length = "-" if stats.best_path_length is None else str(stats.best_path_length)
    minotaur_unique = (
        "-" if stats.best_minotaur_unique_cells is None else str(stats.best_minotaur_unique_cells)
    )
    print(
        f"{stats.generation:>3} | "
        f"{stats.best_human_fitness:>10.1f} | "
        f"{stats.average_human_fitness:>9.1f} | "
        f"{stats.best_minotaur_fitness:>13.1f} | "
        f"{stats.average_minotaur_fitness:>12.1f} | "
        f"{stats.average_escaped:>3.1f} | "
        f"{stats.average_caught:>6.1f} | "
        f"{stats.average_timed_out:>7.1f} | "
        f"{path_length:>9} | "
        f"{minotaur_unique:>11}"
    )


def write_csv(path: Path, history: list[GenerationStats]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "generation",
                "best_human_fitness",
                "average_human_fitness",
                "best_minotaur_fitness",
                "average_minotaur_fitness",
                "average_escaped",
                "average_caught",
                "average_timed_out",
                "best_path_length",
                "best_minotaur_path_length",
                "best_minotaur_unique_cells",
            ]
        )
        for stats in history:
            writer.writerow(
                [
                    stats.generation,
                    stats.best_human_fitness,
                    stats.average_human_fitness,
                    stats.best_minotaur_fitness,
                    stats.average_minotaur_fitness,
                    stats.average_escaped,
                    stats.average_caught,
                    stats.average_timed_out,
                    stats.best_path_length,
                    stats.best_minotaur_path_length,
                    stats.best_minotaur_unique_cells,
                ]
            )


if __name__ == "__main__":
    main()
