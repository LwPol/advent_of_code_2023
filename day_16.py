from typing import List, NamedTuple, Tuple, Optional, Set
from enum import Enum
from functools import partial
import sys


Position = Tuple[int, int]

class Layout(NamedTuple):
    values: List[str]
    width: int
    height: int


class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

Beam = Tuple[Position, Direction]


def parse_layout(lines: List[str]):
    return Layout(lines, width=len(lines[0]), height=len(lines))


def is_in_bounds(layout: Layout, position: Position) -> bool:
    return (position[0] >= 0 and position[0] < layout.width
            and position[1] >= 0 and position[1] < layout.height)


def advance_beam(layout: Layout, beam: Beam) -> Optional[Position]:
    pos, direction = beam
    x, y = pos
    if direction == Direction.LEFT:
        new_pos = (x - 1, y)
    elif direction == Direction.RIGHT:
        new_pos = (x + 1, y)
    elif direction == Direction.UP:
        new_pos = (x, y - 1)
    elif direction == Direction.DOWN:
        new_pos = (x, y + 1)
    return new_pos if is_in_bounds(layout, new_pos) else None


def reflect_beam(beam_direction: Beam, mirror: str) -> Direction:
    if beam_direction == Direction.RIGHT:
        return Direction.DOWN if mirror == '\\' else Direction.UP
    elif beam_direction == Direction.LEFT:
        return Direction.UP if mirror == '\\' else Direction.DOWN
    elif beam_direction == Direction.DOWN:
        return Direction.RIGHT if mirror == '\\' else Direction.LEFT
    elif beam_direction == Direction.UP:
        return Direction.LEFT if mirror == '\\' else Direction.RIGHT


def split_beam(beam_direction: Direction, splitter: str) -> Optional[Tuple[Direction, Direction]]:
    if beam_direction == Direction.RIGHT or beam_direction == Direction.LEFT:
        return (Direction.UP, Direction.DOWN) if splitter == '|' else None
    else:
        return (Direction.LEFT, Direction.RIGHT) if splitter == '-' else None


def follow_beam(layout: Layout, beam: Beam, cache: Set[Beam]):
    if beam in cache:
        return
    
    pos, direction = beam
    x, y = pos
    cache.add(beam)

    current = layout.values[y][x]
    if current == '.':
        next_pos = advance_beam(layout, beam)
        if next_pos is not None:
            follow_beam(layout, (next_pos, direction), cache)
    elif current == '\\' or current == '/':
        reflected = (pos, reflect_beam(direction, current))
        next_pos = advance_beam(layout, reflected)
        if next_pos is not None:
            follow_beam(layout, (next_pos, reflected[1]), cache)
    elif current == '-' or current == '|':
        splitted = split_beam(direction, current)
        if splitted:
            follow_beam(layout, (pos, splitted[0]), cache)
            return follow_beam(layout, (pos, splitted[1]), cache)
        next_pos = advance_beam(layout, beam)
        if next_pos is not None:
            follow_beam(layout, (next_pos, direction), cache)


def count_energised_tiles(layout: Layout, starting_beam: Beam) -> int:
    cache = set()
    follow_beam(layout, starting_beam, cache)
    return len({beam[0] for beam in cache})


def find_best_outcome(layout: Layout):
    def enumerate_starting_beams():
        for i in range(layout.width):
            yield ((i, 0), Direction.DOWN)
            yield ((i, layout.height - 1), Direction.UP)
        for i in range(layout.height):
            yield ((0, i), Direction.RIGHT)
            yield ((layout.width - 1, i), Direction.LEFT)
    return max(*map(partial(count_energised_tiles, layout), enumerate_starting_beams()))


def resolve_part1(input):
    sys.setrecursionlimit(10000)
    return count_energised_tiles(parse_layout(input), starting_beam=((0, 0), Direction.RIGHT))


def resolve_part2(input):
    sys.setrecursionlimit(10000)
    return find_best_outcome(parse_layout(input))