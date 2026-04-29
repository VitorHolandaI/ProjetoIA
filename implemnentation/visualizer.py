from __future__ import annotations
import time

from .dna import MinotaurDNA
from .fitness import score_human, score_minotaurs
from .models import GenerationStats, HumanAgent, HumanRunEvent, MinotaurAgent, TrialResult
from .pygame_finish import wait_on_finish
from .simulation import LabyrinthEvolution
from .trial_helpers import add_scores, best_escaped_path, or_flags


class TerminalVisualizer:
    def __init__(self, evolution: LabyrinthEvolution, fps: float, use_color: bool) -> None:
        self.evolution = evolution
        self.fps = fps
        self.use_color = use_color

    def run(self) -> list[GenerationStats]:
        history: list[GenerationStats] = []
        self._hide_cursor()
        try:
            for generation in range(1, self.evolution.config.generations + 1):
                stats = self._run_visual_generation(generation)
                history.append(stats)
                self._draw_generation_summary(stats)
                self._sleep(1.1)
        finally:
            self._show_cursor()
        return history
    def _run_visual_generation(self, generation: int) -> GenerationStats:
        human_totals = [0.0 for _ in self.evolution.human_population]
        human_parent_flags = [False for _ in self.evolution.human_population]
        minotaur_scores: list[float] = []
        events: list[HumanRunEvent] = []
        escaped = caught = timed_out = 0
        for trial_index, minotaur_dna in enumerate(self.evolution.minotaur_population):
            if trial_index == 0:
                result = self._run_visual_trial(generation, minotaur_dna)
            else:
                result = self.evolution._run_trial(minotaur_dna)
            human_totals = add_scores(human_totals, result.human_scores)
            human_parent_flags = or_flags(human_parent_flags, result.human_escaped_flags)
            minotaur_scores.append(result.minotaur_score)
            events.extend(result.human_events)
            escaped += result.escaped_count
            caught += result.caught_count
            timed_out += result.timed_out_count
            self.evolution._record_best_path(result.best_path)
        self.evolution._record_generation_knowledge(events)
        human_scores = [score / len(self.evolution.minotaur_population) for score in human_totals]
        stats = self.evolution._build_stats(
            generation,
            human_scores,
            minotaur_scores,
            escaped,
            caught,
            timed_out,
        )
        self.evolution._breed_next_generation(human_scores, human_parent_flags, minotaur_scores)
        return stats
    def _run_visual_trial(self, generation: int, minotaur_dna: MinotaurDNA) -> TrialResult:
        humans = self.evolution._spawn_humans()
        minotaurs = self.evolution._spawn_minotaurs(minotaur_dna)
        scent = self.evolution._create_scent_map()
        self.evolution._deposit_human_scent(humans, scent)
        self._draw_trial(generation, 0, humans, minotaurs)
        last_step = 0
        for step in range(1, self.evolution.config.max_steps + 1):
            last_step = step
            self.evolution._advance_trial_step(humans, minotaurs, scent, step)
            self._draw_trial(generation, step, humans, minotaurs)
            if all(not human.is_alive for human in humans):
                break
        self.evolution._mark_timeouts(humans)
        self._draw_trial(generation, last_step, humans, minotaurs)
        self.evolution._record_best_minotaur_path(minotaurs)
        human_scores = [score_human(self.evolution.config, self.evolution.maze, human) for human in humans]
        self.evolution._record_best_human_score_path(humans, human_scores)
        return TrialResult(
            human_scores=human_scores,
            human_escaped_flags=[human.escaped for human in humans],
            human_events=[self.evolution._make_human_event(human) for human in humans],
            minotaur_score=score_minotaurs(
                self.evolution.config,
                self.evolution.maze,
                self.evolution.knowledge,
                minotaurs,
                humans,
            ),
            escaped_count=sum(1 for human in humans if human.escaped),
            caught_count=sum(1 for human in humans if human.caught),
            timed_out_count=sum(1 for human in humans if human.timed_out),
            best_path=best_escaped_path(humans),
        )
    def _draw_trial(
        self,
        generation: int,
        step: int,
        humans: list[HumanAgent],
        minotaurs: list[MinotaurAgent],
    ) -> None:
        self._clear()
        print(
            f"Generation {generation} | "
            f"Time {step}/{self.evolution.config.max_steps} | "
            f"Remaining {self._time_remaining(step)}"
        )
        print(self._render_grid(humans, minotaurs))
        print()
        print(self._trial_stats(humans))
        print("Legend: H human | M Minotaur | digits mean stacked agents | X exit")
        self._sleep(1.0 / self.fps if self.fps > 0 else 0.0)
    def _render_grid(self, humans: list[HumanAgent], minotaurs: list[MinotaurAgent]) -> str:
        alive_counts = self._alive_human_counts(humans)
        minotaur_counts = self._minotaur_counts(minotaurs)
        rows: list[str] = []
        for y, row in enumerate(self.evolution.maze.grid):
            cells: list[str] = []
            for x, cell in enumerate(row):
                position = (x, y)
                if position in minotaur_counts:
                    cells.append(self._minotaur_cell(minotaur_counts[position]))
                elif position in alive_counts:
                    cells.append(self._human_cell(alive_counts[position]))
                elif cell == "#":
                    cells.append(self._color("#", "37"))
                elif cell == "X":
                    cells.append(self._color("X", "32"))
                elif cell == "S":
                    cells.append(self._color("S", "36"))
                elif cell.isalpha():
                    cells.append(self._color(cell, "33"))
                else:
                    cells.append(".")
            rows.append("".join(cells))
        return "\n".join(rows)
    def _alive_human_counts(self, humans: list[HumanAgent]) -> dict[tuple[int, int], int]:
        counts: dict[tuple[int, int], int] = {}
        for human in humans:
            if human.is_alive:
                counts[human.position] = counts.get(human.position, 0) + 1
        return counts
    def _human_cell(self, count: int) -> str:
        if count == 1:
            return self._color("H", "34")
        return self._color(str(min(count, 9)), "34")
    def _minotaur_cell(self, count: int) -> str:
        if count == 1:
            return self._color("M", "31")
        return self._color(str(min(count, 9)), "31")
    def _minotaur_counts(self, minotaurs: list[MinotaurAgent]) -> dict[tuple[int, int], int]:
        counts: dict[tuple[int, int], int] = {}
        for minotaur in minotaurs:
            counts[minotaur.position] = counts.get(minotaur.position, 0) + 1
        return counts
    def _trial_stats(self, humans: list[HumanAgent]) -> str:
        alive = sum(1 for human in humans if human.is_alive)
        escaped = sum(1 for human in humans if human.escaped)
        caught = sum(1 for human in humans if human.caught)
        timed_out = sum(1 for human in humans if human.timed_out)
        return f"Alive: {alive} | Escaped: {escaped} | Caught: {caught} | Timed out: {timed_out}"
    def _draw_generation_summary(self, stats: GenerationStats) -> None:
        self._clear()
        path_length = "-" if stats.best_path_length is None else str(stats.best_path_length)
        print(f"Generation {stats.generation} finished")
        print(f"Human best fitness:    {stats.best_human_fitness:.1f}")
        print(f"Human average fitness: {stats.average_human_fitness:.1f}")
        print(f"Minotaur best fitness: {stats.best_minotaur_fitness:.1f}")
        print(f"Average escaped:       {stats.average_escaped:.1f}")
        print(f"Average caught:        {stats.average_caught:.1f}")
        print(f"Best path length:      {path_length}")
        print(f"Minotaur unique cells: {stats.best_minotaur_unique_cells or '-'}")
    def _clear(self) -> None:
        print("\x1b[2J\x1b[H", end="")
    def _hide_cursor(self) -> None:
        print("\x1b[?25l", end="")
    def _show_cursor(self) -> None:
        print("\x1b[?25h", end="")
    def _color(self, text: str, color_code: str) -> str:
        if not self.use_color:
            return text
        return f"\x1b[{color_code}m{text}\x1b[0m"
    def _time_remaining(self, step: int) -> int:
        return max(0, self.evolution.config.max_steps - step)

    def _sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


def run_visual_evolution(
    evolution: LabyrinthEvolution,
    fps: float,
    use_color: bool,
) -> list[GenerationStats]:
    return TerminalVisualizer(evolution, fps, use_color).run()


class PygameVisualizer:
    panel_width = 300

    def __init__(
        self,
        evolution: LabyrinthEvolution,
        fps: float,
        tile_size: int,
        pygame_module,
    ) -> None:
        self.evolution = evolution
        self.fps = fps
        self.tile_size = tile_size
        self.pygame = pygame_module
        self.running = True
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None

    def run(self) -> list[GenerationStats]:
        self._setup_window()
        history: list[GenerationStats] = []
        for generation in range(1, self.evolution.config.generations + 1):
            if not self.running:
                break
            stats = self._run_pygame_generation(generation)
            history.append(stats)
            self._show_generation_summary(stats)
        if history and self.running:
            wait_on_finish(self.pygame, self.screen, self.clock, self.font, self.small_font, history[-1])
        self.pygame.quit()
        return history

    def _setup_window(self) -> None:
        self.pygame.init()
        maze = self.evolution.maze
        width = maze.width * self.tile_size + self.panel_width
        height = max(maze.height * self.tile_size, 420)
        self.screen = self.pygame.display.set_mode((width, height))
        self.pygame.display.set_caption("Minotaur Labyrinth Genetic Algorithm")
        self.clock = self.pygame.time.Clock()
        self.font = self.pygame.font.SysFont("arial", 20)
        self.small_font = self.pygame.font.SysFont("arial", 16)

    def _run_pygame_generation(self, generation: int) -> GenerationStats:
        human_totals = [0.0 for _ in self.evolution.human_population]
        human_parent_flags = [False for _ in self.evolution.human_population]
        minotaur_scores: list[float] = []
        events: list[HumanRunEvent] = []
        escaped = caught = timed_out = 0
        for trial_index, minotaur_dna in enumerate(self.evolution.minotaur_population):
            if trial_index == 0 and self.running:
                result = self._run_pygame_trial(generation, minotaur_dna)
            else:
                result = self.evolution._run_trial(minotaur_dna)
            human_totals = add_scores(human_totals, result.human_scores)
            human_parent_flags = or_flags(human_parent_flags, result.human_escaped_flags)
            minotaur_scores.append(result.minotaur_score)
            events.extend(result.human_events)
            escaped += result.escaped_count
            caught += result.caught_count
            timed_out += result.timed_out_count
            self.evolution._record_best_path(result.best_path)
        self.evolution._record_generation_knowledge(events)
        human_scores = [score / len(self.evolution.minotaur_population) for score in human_totals]
        stats = self.evolution._build_stats(
            generation,
            human_scores,
            minotaur_scores,
            escaped,
            caught,
            timed_out,
        )
        self.evolution._breed_next_generation(human_scores, human_parent_flags, minotaur_scores)
        return stats

    def _run_pygame_trial(self, generation: int, minotaur_dna: MinotaurDNA) -> TrialResult:
        humans = self.evolution._spawn_humans()
        minotaurs = self.evolution._spawn_minotaurs(minotaur_dna)
        scent = self.evolution._create_scent_map()
        self.evolution._deposit_human_scent(humans, scent)
        self._draw_frame(generation, 0, humans, minotaurs)
        for step in range(1, self.evolution.config.max_steps + 1):
            if not self.running:
                break
            self.evolution._advance_trial_step(humans, minotaurs, scent, step)
            self._draw_frame(generation, step, humans, minotaurs)
            if all(not human.is_alive for human in humans):
                break
        self.evolution._mark_timeouts(humans)
        self.evolution._record_best_minotaur_path(minotaurs)
        human_scores = [score_human(self.evolution.config, self.evolution.maze, human) for human in humans]
        self.evolution._record_best_human_score_path(humans, human_scores)
        return TrialResult(
            human_scores=human_scores,
            human_escaped_flags=[human.escaped for human in humans],
            human_events=[self.evolution._make_human_event(human) for human in humans],
            minotaur_score=score_minotaurs(
                self.evolution.config,
                self.evolution.maze,
                self.evolution.knowledge,
                minotaurs,
                humans,
            ),
            escaped_count=sum(1 for human in humans if human.escaped),
            caught_count=sum(1 for human in humans if human.caught),
            timed_out_count=sum(1 for human in humans if human.timed_out),
            best_path=best_escaped_path(humans),
        )

    def _draw_frame(
        self,
        generation: int,
        step: int,
        humans: list[HumanAgent],
        minotaurs: list[MinotaurAgent],
    ) -> None:
        self._handle_events()
        if not self.running:
            return
        self.screen.fill((246, 244, 238))
        self._draw_maze()
        self._draw_humans(humans)
        self._draw_minotaurs(minotaurs)
        self._draw_panel(generation, step, humans)
        self.pygame.display.flip()
        if self.fps > 0:
            self.clock.tick(self.fps)

    def _draw_maze(self) -> None:
        for y, row in enumerate(self.evolution.maze.grid):
            for x, cell in enumerate(row):
                rect = self._tile_rect(x, y)
                color = self._cell_color(cell)
                self.pygame.draw.rect(self.screen, color, rect)
                self.pygame.draw.rect(self.screen, (190, 184, 174), rect, 1)
                if cell.isalpha() and cell not in {"S", "X"}:
                    self._draw_centered_text(cell, rect, (74, 55, 16))

    def _draw_humans(self, humans: list[HumanAgent]) -> None:
        counts = self._alive_human_counts(humans)
        for position, count in counts.items():
            center = self._tile_center(position)
            radius = max(5, self.tile_size // 4)
            self.pygame.draw.circle(self.screen, (38, 111, 220), center, radius)
            if count > 1:
                label = str(min(count, 9))
                self._draw_centered_text(label, self._tile_rect(*position), (255, 255, 255))

    def _draw_minotaurs(self, minotaurs: list[MinotaurAgent]) -> None:
        counts = self._minotaur_counts(minotaurs)
        for position, count in counts.items():
            rect = self._tile_rect(*position)
            center = self._tile_center(position)
            radius = max(7, self.tile_size // 3)
            self.pygame.draw.circle(self.screen, (188, 43, 43), center, radius)
            label = "M" if count == 1 else str(min(count, 9))
            self._draw_centered_text(label, rect, (255, 255, 255))

    def _draw_panel(self, generation: int, step: int, humans: list[HumanAgent]) -> None:
        panel_x = self.evolution.maze.width * self.tile_size
        panel_rect = self.pygame.Rect(panel_x, 0, self.panel_width, self.screen.get_height())
        self.pygame.draw.rect(self.screen, (34, 36, 40), panel_rect)
        alive = sum(1 for human in humans if human.is_alive)
        escaped = sum(1 for human in humans if human.escaped)
        caught = sum(1 for human in humans if human.caught)
        timed_out = sum(1 for human in humans if human.timed_out)
        best_path = "-" if self.evolution.best_path is None else str(len(self.evolution.best_path))
        minotaur_unique = (
            "-"
            if self.evolution.best_minotaur_path is None
            else str(len(set(self.evolution.best_minotaur_path)))
        )
        lines = [
            "Minotaur Labyrinth GA",
            f"Generation: {generation}",
            f"Time: {step}/{self.evolution.config.max_steps}",
            f"Remaining: {self._time_remaining(step)}",
            f"Alive: {alive}",
            f"Escaped: {escaped}",
            f"Caught: {caught}",
            f"Timed out: {timed_out}",
            f"Best path: {best_path}",
            f"Minotaur unique: {minotaur_unique}",
            "",
            "Blue: humans",
            "Red: Minotaur",
            "Numbers: stacked agents",
            "Green: exit",
            "Yellow: landmarks",
            "",
            "Close window or press Esc",
        ]
        y = 18
        for index, line in enumerate(lines):
            color = (255, 255, 255) if index == 0 else (225, 228, 232)
            font = self.font if index == 0 else self.small_font
            self.screen.blit(font.render(line, True, color), (panel_x + 18, y))
            y += 30 if index == 0 else 24

    def _show_generation_summary(self, stats: GenerationStats) -> None:
        if not self.running:
            return
        frames = int(max(1, self.fps) * 1.0) if self.fps > 0 else 1
        for _ in range(frames):
            self._handle_events()
            if not self.running:
                return
            self.screen.fill((34, 36, 40))
            path_length = "-" if stats.best_path_length is None else str(stats.best_path_length)
            lines = [
                f"Generation {stats.generation} finished",
                f"Human best fitness: {stats.best_human_fitness:.1f}",
                f"Human average fitness: {stats.average_human_fitness:.1f}",
                f"Minotaur best fitness: {stats.best_minotaur_fitness:.1f}",
                f"Average escaped: {stats.average_escaped:.1f}",
                f"Average caught: {stats.average_caught:.1f}",
                f"Best path length: {path_length}",
                f"Minotaur unique cells: {stats.best_minotaur_unique_cells or '-'}",
            ]
            self._draw_summary_lines(lines)
            self.pygame.display.flip()
            if self.fps > 0:
                self.clock.tick(self.fps)

    def _draw_summary_lines(self, lines: list[str]) -> None:
        x = 28
        y = 28
        for index, line in enumerate(lines):
            font = self.font if index == 0 else self.small_font
            color = (255, 255, 255) if index == 0 else (225, 228, 232)
            self.screen.blit(font.render(line, True, color), (x, y))
            y += 34 if index == 0 else 26

    def _handle_events(self) -> None:
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.running = False
            elif event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
                self.running = False

    def _time_remaining(self, step: int) -> int:
        return max(0, self.evolution.config.max_steps - step)

    def _alive_human_counts(self, humans: list[HumanAgent]) -> dict[tuple[int, int], int]:
        counts: dict[tuple[int, int], int] = {}
        for human in humans:
            if human.is_alive:
                counts[human.position] = counts.get(human.position, 0) + 1
        return counts

    def _minotaur_counts(self, minotaurs: list[MinotaurAgent]) -> dict[tuple[int, int], int]:
        counts: dict[tuple[int, int], int] = {}
        for minotaur in minotaurs:
            counts[minotaur.position] = counts.get(minotaur.position, 0) + 1
        return counts

    def _cell_color(self, cell: str) -> tuple[int, int, int]:
        if cell == "#":
            return (35, 38, 42)
        if cell == "S":
            return (91, 192, 190)
        if cell == "X":
            return (81, 168, 91)
        if cell.isalpha():
            return (232, 195, 92)
        return (232, 226, 216)

    def _tile_rect(self, x: int, y: int):
        return self.pygame.Rect(
            x * self.tile_size,
            y * self.tile_size,
            self.tile_size,
            self.tile_size,
        )

    def _tile_center(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        return (
            x * self.tile_size + self.tile_size // 2,
            y * self.tile_size + self.tile_size // 2,
        )

    def _draw_centered_text(self, text: str, rect, color: tuple[int, int, int]) -> None:
        rendered = self.small_font.render(text, True, color)
        text_rect = rendered.get_rect(center=rect.center)
        self.screen.blit(rendered, text_rect)


def run_pygame_evolution(
    evolution: LabyrinthEvolution,
    fps: float,
    tile_size: int,
) -> list[GenerationStats]:
    try:
        import pygame
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Pygame is not installed. Run `UV_CACHE_DIR=/tmp/uv-cache uv pip install pygame` first."
        ) from error
    return PygameVisualizer(evolution, fps, tile_size, pygame).run()
