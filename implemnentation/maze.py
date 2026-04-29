from collections import deque
from dataclasses import dataclass

Position = tuple[int, int]

DEFAULT_GRID = (
    "###############",
    "#S.K..#...A.L.#",
    "###.#.#.#.###.#",
    "#FM.#.N.#G..#.#",
    "#.#####.###.#.#",
    "#.#B.O#.P.#..Q#",
    "#.#.#.###.###.#",
    "#R..#...#C.U#.#",
    "#.#####.###.#.#",
    "#..H..#T..#I..#",
    "###.#.###.###.#",
    "#D..#.....#...#",
    "#.#######.#.#.#",
    "#..J..E...#..X#",
    "###############",
)

SPIRAL_GRID = (
    "###############",
    "#SK.F...#..L.X#",
    "######.#.###.##",
    "#A.M...#..N#..#",
    "#.########.#.##",
    "#..G.O.P.#.#..#",
    "#.#.####.#.##.#",
    "#.#.#B.Q.#C.#.#",
    "#.#.######.#..#",
    "#.#..H..R..##.#",
    "#.##########..#",
    "#D.U..I..T....#",
    "#.###########.#",
    "#..J..E.......#",
    "###############",
)

BRANCH_GRID = (
    "###############",
    "#S.K..A..L.#..#",
    "###.#####.#.#.#",
    "#FM.#.N.#.#.#.#",
    "#.###.#.#.#.#.#",
    "#O..#.#.G.#..P#",
    "###.#.#######.#",
    "#B.Q#..R..C.#.#",
    "#.#######.#.#.#",
    "#..H..#.U.#I.T#",
    "#.###.#.#####.#",
    "#D#...#.....#.#",
    "#.#.#######.#.#",
    "#...E..J....#X#",
    "###############",
)

RING_GRID = (
    "###############",
    "#S.KF.#..L....#",
    "#.###.#.#####.#",
    "#A#M..#..N..#.#",
    "#.#.#######.#.#",
    "#.#.O..PB.#.#.#",
    "#.#####.#.#.#.#",
    "#..G.Q#.#C#..R#",
    "#####.#.#.###.#",
    "#DU.H.#.#..IT.#",
    "#.#####.#####.#",
    "#.....#.....#.#",
    "#.###.#####.#.#",
    "#...E..J....#X#",
    "###############",
)

OPEN_GRID = (
    "###############",
    "#S..#.....#...#",
    "#.#.#.###.#.#.#",
    "#.#A..#...#.#.#",
    "#.#####.###.#.#",
    "#.....#...#.#.#",
    "###.#.###.#.#.#",
    "#B..#...#C..#.#",
    "#.#####.#####.#",
    "#...#.......#.#",
    "#.#.#.#####.#.#",
    "#.#D#.....#...#",
    "#.#.#####.###.#",
    "#...E.......#X#",
    "###############",
)

CROSSROADS_GRID = (
    "###############",
    "#S.K#F.L#....X#",
    "#.#.#.#.#.#.#.#",
    "#.#.M.#A#.N.#.#",
    "#.#####.#####.#",
    "#O.G..#.#.PH..#",
    "###.#.#.#.#.###",
    "#B.Q#..RC.....#",
    "###.#.#.#.#.###",
    "#..I.U#.#..T..#",
    "#.#####.#####.#",
    "#.#...#D#...#.#",
    "#.#.#.#.#.#.#.#",
    "#E..#..J....#.#",
    "###############",
)

MAZE_GRIDS = {
    1: ("Classic", DEFAULT_GRID, (7, 7)),
    2: ("Spiral", SPIRAL_GRID, (7, 7)),
    3: ("Branches", BRANCH_GRID, (7, 7)),
    4: ("Rings", RING_GRID, (7, 7)),
    5: ("Crossroads", CROSSROADS_GRID, (7, 7)),
}

LANDMARK_NAMES = {
    "A": "torch hall",
    "B": "broken statue",
    "C": "blue fountain",
    "D": "cracked wall",
    "E": "bronze door",
    "F": "red banner",
    "G": "stone altar",
    "H": "bone pile",
    "I": "silver mirror",
    "J": "old well",
    "K": "black obelisk",
    "L": "gold mask",
    "M": "hanging chain",
    "N": "painted eye",
    "O": "dry roots",
    "P": "ash circle",
    "Q": "fallen shield",
    "R": "white column",
    "T": "green flame",
    "U": "marked gate",
}


@dataclass(frozen=True)
class Maze:
    grid: tuple[str, ...]
    entrances: tuple[Position, ...]
    exit_position: Position
    landmarks: dict[str, Position]
    minotaur_start: Position

    @classmethod
    def default(cls) -> "Maze":
        return cls.by_id(1)

    @classmethod
    def by_id(cls, maze_id: int) -> "Maze":
        if maze_id not in MAZE_GRIDS:
            raise ValueError(f"Unknown maze_id {maze_id}; expected one of {sorted(MAZE_GRIDS)}")
        _, grid, minotaur_start = MAZE_GRIDS[maze_id]
        return cls.from_grid(grid, minotaur_start=minotaur_start)

    @classmethod
    def from_grid(cls, grid: tuple[str, ...], minotaur_start: Position) -> "Maze":
        width = len(grid[0])
        if any(len(row) != width for row in grid):
            raise ValueError("Maze rows must all have the same width")
        entrances: list[Position] = []
        landmarks: dict[str, Position] = {}
        exit_position: Position | None = None
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                position = (x, y)
                if cell == "S":
                    entrances.append(position)
                elif cell == "X":
                    exit_position = position
                elif cell in LANDMARK_NAMES:
                    landmarks[cell] = position
        if exit_position is None:
            raise ValueError("Maze must contain one X exit cell")
        if not entrances:
            raise ValueError("Maze must contain at least one S entrance cell")
        maze = cls(grid, tuple(entrances), exit_position, landmarks, minotaur_start)
        if not maze.is_walkable(minotaur_start):
            raise ValueError(f"Minotaur start {minotaur_start} must be walkable")
        if maze.reachable_positions(minotaur_start) != maze.walkable_positions():
            raise ValueError("All walkable cells must be connected to the Minotaur start")
        return maze

    @property
    def width(self) -> int:
        return len(self.grid[0])

    @property
    def height(self) -> int:
        return len(self.grid)

    def cell_at(self, position: Position) -> str:
        x, y = position
        return self.grid[y][x]

    def is_walkable(self, position: Position) -> bool:
        x, y = position
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.cell_at(position) != "#"

    def neighbors(self, position: Position) -> list[Position]:
        x, y = position
        candidates = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        return [candidate for candidate in candidates if self.is_walkable(candidate)]

    def walkable_positions(self) -> set[Position]:
        return {
            (x, y)
            for y, row in enumerate(self.grid)
            for x, cell in enumerate(row)
            if cell != "#"
        }

    def reachable_positions(self, start: Position) -> set[Position]:
        queue: deque[Position] = deque([start])
        visited = {start}
        while queue:
            position = queue.popleft()
            for neighbor in self.neighbors(position):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def landmark_at(self, position: Position) -> str | None:
        for landmark_id, landmark_position in self.landmarks.items():
            if landmark_position == position:
                return landmark_id
        return None

    def visible_landmarks(self, position: Position, radius: int) -> list[str]:
        visible: list[str] = []
        for landmark_id, landmark_position in self.landmarks.items():
            if manhattan(position, landmark_position) <= radius:
                visible.append(landmark_id)
        return visible

    def line_of_sight(self, left: Position, right: Position) -> bool:
        if left[0] == right[0]:
            return self._clear_vertical_view(left, right)
        if left[1] == right[1]:
            return self._clear_horizontal_view(left, right)
        return False

    def _clear_vertical_view(self, left: Position, right: Position) -> bool:
        x = left[0]
        start_y, end_y = sorted((left[1], right[1]))
        for y in range(start_y + 1, end_y):
            if self.cell_at((x, y)) == "#":
                return False
        return True

    def _clear_horizontal_view(self, left: Position, right: Position) -> bool:
        y = left[1]
        start_x, end_x = sorted((left[0], right[0]))
        for x in range(start_x + 1, end_x):
            if self.cell_at((x, y)) == "#":
                return False
        return True

    def shortest_distance(self, start: Position, goal: Position) -> int:
        queue: deque[tuple[Position, int]] = deque([(start, 0)])
        visited = {start}
        while queue:
            position, distance = queue.popleft()
            if position == goal:
                return distance
            for neighbor in self.neighbors(position):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        return self.width * self.height

    def render_path(self, path: list[Position]) -> str:
        path_positions = set(path)
        rows: list[str] = []
        for y, row in enumerate(self.grid):
            cells: list[str] = []
            for x, cell in enumerate(row):
                position = (x, y)
                if position in path_positions and cell not in {"S", "X"}:
                    cells.append("*")
                else:
                    cells.append(cell)
            rows.append("".join(cells))
        return "\n".join(rows)


def manhattan(left: Position, right: Position) -> int:
    return abs(left[0] - right[0]) + abs(left[1] - right[1])
