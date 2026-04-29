from .maze import MAZE_GRIDS, Maze


class MazeSelector:
    card_width = 190
    card_height = 230
    preview_cell = 10
    margin = 24

    def __init__(self, pygame_module) -> None:
        self.pygame = pygame_module
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None

    def choose(self) -> Maze | None:
        self._setup()
        while True:
            selected = self._handle_events()
            if selected == 0:
                self.pygame.quit()
                return None
            if selected is not None:
                self.pygame.quit()
                return Maze.by_id(selected)
            self._draw()
            self.clock.tick(30)

    def _setup(self) -> None:
        self.pygame.init()
        self.screen = self.pygame.display.set_mode((700, 610))
        self.pygame.display.set_caption("Choose Labyrinth")
        self.clock = self.pygame.time.Clock()
        self.font = self.pygame.font.SysFont("arial", 24)
        self.small_font = self.pygame.font.SysFont("arial", 16)

    def _handle_events(self) -> int | None:
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                return 0
            if event.type == self.pygame.KEYDOWN:
                selected = self._key_selection(event.key)
                if selected is not None:
                    return selected
                if event.key == self.pygame.K_ESCAPE:
                    return 0
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = self._clicked_maze(event.pos)
                if clicked is not None:
                    return clicked
        return None

    def _draw(self) -> None:
        self.screen.fill((31, 34, 39))
        self._draw_header()
        mouse_position = self.pygame.mouse.get_pos()
        for maze_id, (name, grid, _) in MAZE_GRIDS.items():
            rect = self._card_rect(maze_id)
            hovered = rect.collidepoint(mouse_position)
            self._draw_card(rect, maze_id, name, grid, hovered)
        self.pygame.display.flip()

    def _draw_header(self) -> None:
        title = self.font.render("Choose a labyrinth", True, (255, 255, 255))
        subtitle = self.small_font.render("Click a map or press 1-5", True, (210, 214, 220))
        self.screen.blit(title, (24, 20))
        self.screen.blit(subtitle, (24, 52))

    def _draw_card(
        self,
        rect,
        maze_id: int,
        name: str,
        grid: tuple[str, ...],
        hovered: bool,
    ) -> None:
        border = (91, 192, 190) if hovered else (85, 91, 101)
        self.pygame.draw.rect(self.screen, (45, 49, 56), rect, border_radius=8)
        self.pygame.draw.rect(self.screen, border, rect, width=2, border_radius=8)
        label = self.small_font.render(f"{maze_id}. {name}", True, (255, 255, 255))
        self.screen.blit(label, (rect.x + 14, rect.y + 12))
        self._draw_preview(grid, rect.x + 20, rect.y + 46)

    def _draw_preview(self, grid: tuple[str, ...], start_x: int, start_y: int) -> None:
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                color = self._cell_color(cell)
                rect = self.pygame.Rect(
                    start_x + x * self.preview_cell,
                    start_y + y * self.preview_cell,
                    self.preview_cell,
                    self.preview_cell,
                )
                self.pygame.draw.rect(self.screen, color, rect)

    def _clicked_maze(self, position: tuple[int, int]) -> int | None:
        for maze_id in MAZE_GRIDS:
            if self._card_rect(maze_id).collidepoint(position):
                return maze_id
        return None

    def _card_rect(self, maze_id: int):
        positions = {
            1: (24, 92),
            2: (254, 92),
            3: (484, 92),
            4: (139, 350),
            5: (369, 350),
        }
        x, y = positions[maze_id]
        return self.pygame.Rect(x, y, self.card_width, self.card_height)

    def _key_selection(self, key: int) -> int | None:
        key_map = {
            self.pygame.K_1: 1,
            self.pygame.K_2: 2,
            self.pygame.K_3: 3,
            self.pygame.K_4: 4,
            self.pygame.K_5: 5,
        }
        return key_map.get(key)

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


def choose_maze_with_pygame() -> Maze | None:
    try:
        import pygame
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Pygame is not installed. Run `UV_CACHE_DIR=/tmp/uv-cache uv pip install pygame` first."
        ) from error
    return MazeSelector(pygame).choose()
