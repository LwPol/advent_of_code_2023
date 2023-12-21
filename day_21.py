from typing import NamedTuple, List, Tuple, Iterator, Callable
import itertools
from heapq import heappop, heappush


class Grid(NamedTuple):
    content: List[str]
    width: int
    height: int


Position = Tuple[int, int]
Point = Tuple[int, int]


def parse_grid(lines: List[str]) -> Grid:
    return Grid(lines, len(lines[0]), len(lines))


def find_starting_position(grid: Grid) -> Position:
    for i, j in itertools.product(range(grid.width), range(grid.height)):
        if grid.content[j][i] == 'S':
            return i, j


def continue_for_finite_grid(grid: Grid, position: Position) -> Iterator[Position]:
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    x, y = position
    for dx, dy in dirs:
        xx, yy = x + dx, y + dy
        if (xx >= 0 and xx < grid.width and yy >= 0 and yy < grid.height
            and grid.content[yy][xx] != '#'):
            yield xx, yy


def continue_for_infinite_grid(grid: Grid, position: Position) -> Iterator[Position]:
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    x, y = position
    for dx, dy in dirs:
        xx, yy = x + dx, y + dy
        xmod = xx % grid.width
        ymod = yy % grid.height
        if grid.content[ymod][xmod] != '#':
            yield xx, yy


class DijkstraAlgorithm:
    class QueueItem:
        def __init__(self, node: Position, distance: int):
            self.node = node
            self.distance = distance
        
        def __lt__(self, other) -> bool:
            return self.distance < other.distance

    def __init__(self, grid: Grid,
                 continuation_callback: Callable[[Grid, Position], Iterator[Position]]):
        self.grid = grid
        self.__continue = continuation_callback
    
    def run_algorithm(self, start: Position, step_limit: int) -> int:
        queue = [self.QueueItem(start, 0)]
        visited = set()
        reachable = 0
        steps_mod = step_limit % 2
        while queue:
            next_node = heappop(queue)
            if next_node.distance > step_limit:
                break
            if next_node.node in visited:
                continue
            visited.add(next_node.node)
            if next_node.distance % 2 == steps_mod:
                reachable += 1
            for neigh in self.__continue(self.grid, next_node.node):
                heappush(queue, self.QueueItem(neigh, next_node.distance + 1))
        return reachable


def find_interpolation_points(grid: Grid) -> Tuple[Point, Point, Point]:
    # starting position is at the middle of square grid
    start = find_starting_position(grid)
    algo = DijkstraAlgorithm(grid, continue_for_infinite_grid)
    y1 = algo.run_algorithm(start, step_limit=start[0])
    y2 = algo.run_algorithm(start, step_limit=start[0] + grid.width)
    y3 = algo.run_algorithm(start, step_limit=start[0] + 2 * grid.width)
    return (0, y1), (1, y2), (2, y3)


def determinant(matrix_cols: List[List[int]]) -> int:
    return (
        matrix_cols[0][0] * matrix_cols[1][1] * matrix_cols[2][2] +
        matrix_cols[0][1] * matrix_cols[1][2] * matrix_cols[2][0] +
        matrix_cols[0][2] * matrix_cols[1][0] * matrix_cols[2][1] -
        matrix_cols[0][2] * matrix_cols[1][1] * matrix_cols[2][0] -
        matrix_cols[0][1] * matrix_cols[1][0] * matrix_cols[2][2] -
        matrix_cols[0][0] * matrix_cols[1][2] * matrix_cols[2][1]
    )


def calculate_quadratic_coeffs(grid: Grid) -> Tuple[int, int, int]:
    p1, p2, p3 = find_interpolation_points(grid)
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    col1 = [x1 ** 2, x2 ** 2, x3 ** 2]
    col2 = [x1, x2, x3]
    col3 = [1, 1, 1]
    col_sub = [y1, y2, y3]
    main = determinant([col1, col2, col3])
    a = determinant([col_sub, col2, col3]) // main
    b = determinant([col1, col_sub, col3]) // main
    c = determinant([col1, col2, col_sub]) // main
    return a, b, c


def resolve_part1(input):
    grid = parse_grid(input)
    start_pos = find_starting_position(grid)
    algo = DijkstraAlgorithm(grid, continue_for_finite_grid)
    return algo.run_algorithm(start_pos, step_limit=64)


def resolve_part2(input):
    grid = parse_grid(input)
    a, b, c = calculate_quadratic_coeffs(parse_grid(input))
    size = 26501365 // grid.width
    return a * size ** 2 + b * size + c