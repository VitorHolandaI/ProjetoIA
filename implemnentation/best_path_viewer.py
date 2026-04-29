import os

from .maze import Position
from .simulation import LabyrinthEvolution


def show_best_path_with_pygame(evolution: LabyrinthEvolution, tile_size: int) -> None:
    try:
        import pygame
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Pygame is not installed. Run `UV_CACHE_DIR=/tmp/uv-cache uv pip install pygame` first."
        ) from error
    BestPathViewer(evolution, tile_size, pygame).show()


class BestPathViewer:
    panel_width = 320

    def __init__(self, evolution: LabyrinthEvolution, tile_size: int, pygame_module) -> None:
        self.evolution = evolution
        self.tile_size = tile_size
        self.pygame = pygame_module
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None

    def show(self) -> None:
        self._setup()
        self._draw()
        if os.environ.get("SDL_VIDEODRIVER") != "dummy":
            self._wait_for_close()
        self.pygame.quit()

    def _setup(self) -> None:
        self.pygame.init()
        maze = self.evolution.maze
        width = maze.width * self.tile_size + self.panel_width
        height = max(maze.height * self.tile_size, 420)
        self.screen = self.pygame.display.set_mode((width, height))
        self.pygame.display.set_caption("Best Human Result")
        self.clock = self.pygame.time.Clock()
        self.font = self.pygame.font.SysFont("arial", 22)
        self.small_font = self.pygame.font.SysFont("arial", 16)

    def _wait_for_close(self) -> None:
        running = True
        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
                if event.type == self.pygame.KEYDOWN and event.key in {
                    self.pygame.K_ESCAPE,
                    self.pygame.K_RETURN,
                }:
                    running = False
            self._draw()
            self.clock.tick(30)

    def _draw(self) -> None:
        self.screen.fill((246, 244, 238))
        self._draw_maze()
        self._draw_path()
        self._draw_panel()
        self.pygame.display.flip()

    def _draw_maze(self) -> None:
        for y, row in enumerate(self.evolution.maze.grid):
            for x, cell in enumerate(row):
                rect = self._tile_rect((x, y))
                self.pygame.draw.rect(self.screen, self._cell_color(cell), rect)
                self.pygame.draw.rect(self.screen, (190, 184, 174), rect, 1)
                if cell.isalpha() and cell not in {"S", "X"}:
                    self._draw_centered_text(cell, rect, (74, 55, 16))

    def _draw_path(self) -> None:
        path = self._best_path()
        if not path:
            return
        for index, position in enumerate(path):
            rect = self._tile_rect(position).inflate(-self.tile_size // 3, -self.tile_size // 3)
            color = (44, 132, 90) if index == len(path) - 1 else (38, 111, 220)
            self.pygame.draw.ellipse(self.screen, color, rect)

    def _draw_panel(self) -> None:
        panel_x = self.evolution.maze.width * self.tile_size
        panel_rect = self.pygame.Rect(panel_x, 0, self.panel_width, self.screen.get_height())
        self.pygame.draw.rect(self.screen, (34, 36, 40), panel_rect)
        path = self._best_path()
        path_length = "-" if path is None else str(len(path))
        lines = [
            "Best human result",
            f"Best score: {self.evolution.best_human_score:.1f}",
            f"Path length: {path_length}",
            f"Generations trained: {self.evolution.config.generations}",
            f"Time limit: {self.evolution.config.max_steps}",
            "",
            "Blue dots: best route",
            "Green tile: exit",
            "Yellow tiles: landmarks",
            "",
            "Press Enter, Esc, or close",
        ]
        if path is None:
            lines.insert(1, "No human escaped.")
        y = 20
        for index, line in enumerate(lines):
            font = self.font if index == 0 else self.small_font
            color = (255, 255, 255) if index == 0 else (225, 228, 232)
            self.screen.blit(font.render(line, True, color), (panel_x + 18, y))
            y += 32 if index == 0 else 24

    def _best_path(self) -> list[Position] | None:
        if self.evolution.best_human_score_path is not None:
            return self.evolution.best_human_score_path
        return self.evolution.best_path

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

    def _tile_rect(self, position: Position):
        x, y = position
        return self.pygame.Rect(
            x * self.tile_size,
            y * self.tile_size,
            self.tile_size,
            self.tile_size,
        )

    def _draw_centered_text(self, text: str, rect, color: tuple[int, int, int]) -> None:
        rendered = self.small_font.render(text, True, color)
        text_rect = rendered.get_rect(center=rect.center)
        self.screen.blit(rendered, text_rect)

