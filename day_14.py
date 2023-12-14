from typing import List, Tuple, Set
import itertools
from enum import Enum
from copy import deepcopy


Position = Tuple[int, int]


class TiltDirection(Enum):
    NORTH = 0
    SOUTH = 1
    WEST = 2
    EAST = 3


def parse_rocks_positions(lines: List[str]) -> Tuple[Set[Position], Set[Position]]:
    cubes, rounded = set(), set()
    rev = list(reversed(lines))
    for i, j in itertools.product(range(len(rev[0])), range(len(rev))):
        if rev[j][i] == '#':
            cubes.add((i, j))
        if rev[j][i] == 'O':
            rounded.add((i, j))
    return cubes, rounded


class TiltPlatform:
    def __init__(self, grid: List[str]):
        self.__cubes, self.rounded = parse_rocks_positions(grid)
        self.__vert_obstacles = self.__map_obstacles_for_vertical_dir(grid)
        self.__hor_obstacles = self.__map_obstacles_for_horizontal_dir(grid)
    
    def tilt_cycle(self) -> "TiltPlatform":
        self.tilt(TiltDirection.NORTH)
        self.tilt(TiltDirection.WEST)
        self.tilt(TiltDirection.SOUTH)
        self.tilt(TiltDirection.EAST)
        return self
    
    def tilt(self, direction: TiltDirection) -> Set[Position]:
        if direction == TiltDirection.NORTH:
            rocks = sorted(self.rounded, key=lambda x: x[1], reverse=True)
            vert_obstacles = deepcopy(self.__vert_obstacles)
            self.rounded = {
                self.find_pos_north(rock, vert_obstacles) for rock in rocks
            }
        elif direction == TiltDirection.SOUTH:
            rocks = sorted(self.rounded, key=lambda x: x[1])
            vert_obstacles = deepcopy(self.__vert_obstacles)
            self.rounded = {
                self.find_pos_south(rock, vert_obstacles) for rock in rocks
            }
        elif direction == TiltDirection.EAST:
            rocks = sorted(self.rounded, key=lambda x: x[0], reverse=True)
            hor_obstacles = deepcopy(self.__hor_obstacles)
            self.rounded = {
                self.find_pos_east(rock, hor_obstacles) for rock in rocks
            }
        elif direction == TiltDirection.WEST:
            rocks = sorted(self.rounded, key=lambda x: x[0])
            hor_obstacles = deepcopy(self.__hor_obstacles)
            self.rounded = {
                self.find_pos_west(rock, hor_obstacles) for rock in rocks
            }
        return self.rounded

    def find_pos_north(self, start: Position, obstacles: List[List[int]]) -> Position:
        colliding = obstacles[start[0]]
        stop = next(filter(lambda r: r > start[1], colliding))
        colliding.append(stop - 1)
        colliding.sort()
        return start[0], stop - 1
    
    def find_pos_south(self, start: Position, obstacles: List[List[int]]) -> Position:
        colliding = obstacles[start[0]]
        stop = next(filter(lambda r: r < start[1], reversed(colliding)))
        colliding.append(stop + 1)
        colliding.sort()
        return start[0], stop + 1
    
    def find_pos_east(self, start: Position, obstacles: List[List[int]]) -> Position:
        colliding = obstacles[start[1]]
        stop = next(filter(lambda r: r > start[0], colliding))
        colliding.append(stop - 1)
        colliding.sort()
        return stop - 1, start[1]

    def find_pos_west(self, start: Position, obstacles: List[List[int]]) -> Position:
        colliding = obstacles[start[1]]
        stop = next(filter(lambda r: r < start[0], reversed(colliding)))
        colliding.append(stop + 1)
        colliding.sort()
        return stop + 1, start[1]
    
    def __map_obstacles_for_vertical_dir(self, grid: List[str]) -> List[List[int]]:
        result = [[-1, len(grid)] for _ in range(len(grid[0]))]
        for pos in self.__cubes:
            result[pos[0]].append(pos[1])
        for l in result:
            l.sort()
        return result
    
    def __map_obstacles_for_horizontal_dir(self, grid: List[str]) -> List[List[int]]:
        result = [[-1, len(grid[0])] for _ in range(len(grid))]
        for pos in self.__cubes:
            result[pos[1]].append(pos[0])
        for l in result:
            l.sort()
        return result


def tortoise_and_hare(grid: List[str]) -> Tuple[int, int, TiltPlatform]:
    tortoise = TiltPlatform(grid).tilt_cycle()
    hare = TiltPlatform(grid).tilt_cycle().tilt_cycle()
    while tortoise.rounded != hare.rounded:
        tortoise.tilt_cycle()
        hare.tilt_cycle().tilt_cycle()
    
    mu = 0
    tortoise = TiltPlatform(grid)
    while tortoise.rounded != hare.rounded:
        tortoise.tilt_cycle()
        hare.tilt_cycle()
        mu += 1
    
    lam = 1
    start = set(tortoise.rounded)
    tortoise.tilt_cycle()
    while tortoise.rounded != start:
        tortoise.tilt_cycle()
        lam += 1
    return mu, lam, tortoise


def find_configuration(grid: List[str], steps: int) -> Set[Position]:
    mu, lam, cycle_start = tortoise_and_hare(grid)
    cycle_offset = (steps - mu) % lam
    for _ in range(cycle_offset):
        cycle_start.tilt_cycle()
    return cycle_start.rounded


def calc_rock_load(pos: Position) -> int:
    return pos[1] + 1


def resolve_part1(input):
    return sum(calc_rock_load(r) for r in TiltPlatform(input).tilt(TiltDirection.NORTH))


def resolve_part2(input):
    return sum(calc_rock_load(r) for r in find_configuration(input, steps=1000000000))