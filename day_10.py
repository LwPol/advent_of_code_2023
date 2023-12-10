from typing import List, Iterator, Tuple, Set
import itertools


Grid = List[str]
Position = Tuple[int, int]


def parse_padded_grid(lines: List[str]) -> Grid:
    width = len(lines[0])
    horizontal_padding = ''.join(itertools.repeat('.', width + 2))
    grid = [horizontal_padding]
    grid.extend('.' + line + '.' for line in lines)
    grid.append(horizontal_padding)
    return grid


def get_pipe(grid: Grid, x: int, y: int) -> str:
    return grid[y][x]


def get_neighbours(x: int, y: int) -> Iterator[Tuple[int, int]]:
    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        yield (x + dx, y + dy)


def get_connected_positions(pipe: str, pos: Tuple[int, int]) -> Tuple[Position, Position]:
    x, y = pos
    if pipe == '|':
        return ((x, y - 1), (x, y + 1))
    if pipe == '-':
        return ((x - 1, y), (x + 1, y))
    if pipe == 'L':
        return ((x, y - 1), (x + 1, y))
    if pipe == 'J':
        return ((x, y - 1), (x - 1, y))
    if pipe == '7':
        return ((x, y + 1), (x - 1, y))
    if pipe == 'F':
        return ((x, y + 1), (x + 1, y))
    raise RuntimeError('Invalid pipe: ' + pipe)


def are_connected(grid: Grid, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    dest_pipe = get_pipe(grid, *pos2)
    return dest_pipe != '.' and pos1 in get_connected_positions(dest_pipe, pos2)


def find_start(grid: Grid) -> Position:
    for y, line in enumerate(grid):
        for x, char in enumerate(line):
            if char == 'S':
                return (x, y)


def get_first_pipe_connection(grid: Grid) -> Tuple[Position, Position]:
    start = find_start(grid)
    for pos in get_neighbours(*start):
        if are_connected(grid, start, pos):
            return start, pos


def traverse_loop(grid: Grid) -> List[Position]:
    prev, current = get_first_pipe_connection(grid)
    loop = [prev]
    while get_pipe(grid, *current) != 'S':
        loop.append(current)
        next_pos = next(filter(lambda x: x != prev,
                               get_connected_positions(get_pipe(grid, *current), current)))
        prev = current
        current = next_pos
    return loop


def is_clockwise(grid: Grid, loop: List[Position]) -> bool:
    def is_vertex(pos: Position) -> bool:
        pipe = get_pipe(grid, *pos)
        return pipe != '|' and pipe != '-'
    vertices = list(filter(is_vertex, loop))
    edges = itertools.chain(zip(vertices, vertices[1:]), [(vertices[-1], vertices[0])])
    return sum((p2[0] - p1[0]) * (p2[1] + p1[1]) for p1, p2 in edges) < 0


def right_sides_of_pipes(prev_pos: Position,
                         cur_pos: Position,
                         next_pos: Position) -> Tuple[Position, Position]:
    x, y = cur_pos
    dx, dy = x - prev_pos[0], y - prev_pos[1]
    dx2, dy2 = next_pos[0] - x, next_pos[1] - y
    if dx != 0:
        right1 = (x, y + (1 if dx > 0 else -1))
    else:
        right1 = (x + (1 if dy < 0 else -1), y)
    if dx2 != 0:
        right2 = (x, y + (1 if dx2 > 0 else -1))
    else:
        right2 = (x + (1 if dy2 < 0 else -1), y)
    return (right1, right2)
    

def mark_right_sides_of_pipes(loop: List[Position]) -> Set[Position]:
    loop_parts = set(loop)
    result = set()
    connections = itertools.chain(
        zip(loop, loop[1:], loop[2:]),
        [(loop[-2], loop[-1], loop[0]), (loop[-1], loop[0], loop[1])])
    for prev, current, dest in connections:
        r1, r2 = right_sides_of_pipes(prev, current, dest)
        if r1 not in loop_parts:
            result.add(r1)
        if r2 not in loop_parts:
            result.add(r2)
    return result


def count_tiles_in_loop(grid: Grid) -> int:
    loop = traverse_loop(grid)
    if not is_clockwise(grid, loop):
        loop.reverse()
    loop_parts = set(loop)
    flood_srcs = mark_right_sides_of_pipes(loop)
    flooded = set()
    while flood_srcs:
        flooded.update(flood_srcs)
        next_generation = set()
        for pos in flood_srcs:
            for candidate in get_neighbours(*pos):
                if candidate not in loop_parts and candidate not in flooded:
                    next_generation.add(candidate)
        flood_srcs = next_generation
    return len(flooded)


def resolve_part1(input):
    return len(traverse_loop(parse_padded_grid(input))) // 2


def resolve_part2(input):
    return count_tiles_in_loop(parse_padded_grid(input))