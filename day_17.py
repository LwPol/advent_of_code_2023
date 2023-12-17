from typing import Tuple, List, Callable, Iterator, Set
from heapq import heappush, heappop
from enum import Enum
from functools import partial


class Direction(Enum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3


HeatlossMap = List[List[int]]
Position = Tuple[int, int]
Node = Tuple[Position, Direction, int]


def parse_heatloss_map(lines: List[str]) -> HeatlossMap:
    return [[int(num) for num in row] for row in lines]


def turn_sideways(position: Position,
                  direction: Direction) -> Tuple[Position, Position]:
    x, y = position
    if direction == Direction.RIGHT or direction == Direction.LEFT:
        return (x, y + 1), (x, y - 1)
    elif direction == Direction.DOWN or direction == Direction.UP:
        return (x + 1, y), (x - 1, y)
    raise Exception()


def move_forward(position: Position, direction: Direction) -> Position:
    x, y = position
    if direction == Direction.RIGHT:
        return x + 1, y
    if direction == Direction.LEFT:
        return x - 1, y
    if direction == Direction.DOWN:
        return x, y + 1
    if direction == Direction.UP:
        return x, y - 1
    raise Exception()


def determine_direction(prev_pos: Position, next_pos: Position) -> Direction:
    dx = next_pos[0] - prev_pos[0]
    dy = next_pos[1] - prev_pos[1]
    if dx == 1:
        return Direction.RIGHT
    if dx == -1:
        return Direction.LEFT
    if dy == 1:
        return Direction.DOWN
    if dy == -1:
        return Direction.UP
    raise Exception()


def is_in_bounds(heatlosses: HeatlossMap, position: Position) -> bool:
    x, y = position
    return x >= 0 and x < len(heatlosses[0]) and y >= 0 and y < len(heatlosses)


def continue_path_part1(heatlosses: HeatlossMap, node: Node) -> Iterator[Node]:
    pos, direction, straight = node
    side1, side2 = turn_sideways(pos, direction)
    if is_in_bounds(heatlosses, side1):
        yield side1, determine_direction(pos, side1), 1
    if is_in_bounds(heatlosses, side2):
        yield side2, determine_direction(pos, side2), 1
    if straight < 3:
        forward = move_forward(pos, direction)
        if is_in_bounds(heatlosses, forward):
            yield forward, direction, straight + 1


def check_target_part1(target_pos: Position, node: Node) -> bool:
    return node[0] == target_pos


def continue_path_part2(heatlosses: HeatlossMap, node: Node) -> Iterator[Node]:
    pos, direction, straight = node
    if straight < 10:
        forward = move_forward(pos, direction)
        if is_in_bounds(heatlosses, forward):
            yield forward, direction, straight + 1
    if straight >= 4:
        side1, side2 = turn_sideways(pos, direction)
        if is_in_bounds(heatlosses, side1):
            yield side1, determine_direction(pos, side1), 1
        if is_in_bounds(heatlosses, side2):
            yield side2, determine_direction(pos, side2), 1


def check_target_part2(target_pos: Position, node: Node) -> bool:
    return node[0] == target_pos and node[2] >= 4


def get_target(heatloss_map: HeatlossMap) -> Position:
    return len(heatloss_map[0]) - 1, len(heatloss_map) - 1


class DijkstraAlgorithm:
    class QueueItem:
        def __init__(self, node: Node, distance: int):
            self.node = node
            self.distance = distance
        
        def __lt__(self, other) -> bool:
            return self.distance < other.distance

    def __init__(self,
                 heatloss_map: HeatlossMap,
                 continuations_callback: Callable[[Node], Iterator[Node]],
                 target_node_predicate: Callable[[Node], bool]):
        self.heatloss_map = heatloss_map
        self.__visited: Set[Node] = set()
        self.__continue = continuations_callback
        self.__target_check = target_node_predicate
    
    def run_algorithm(self) -> int:
        starting_pos = (0, 0)
        queue = [self.QueueItem((starting_pos, Direction.RIGHT, 0), 0),
                 self.QueueItem((starting_pos, Direction.DOWN, 0), 0)]
        while queue:
            next_node = heappop(queue)
            if self.__target_check(next_node.node):
                return next_node.distance
            if next_node.node in self.__visited:
                continue
            self.__visited.add(next_node.node)
            for neigh in self.__continue(self.heatloss_map, next_node.node):
                x, y = neigh[0]
                heatloss = self.heatloss_map[y][x]
                heappush(queue, self.QueueItem(neigh, next_node.distance + heatloss))
        raise RuntimeError('Failed to find path')
    

def resolve_part1(input):
    heatloss = parse_heatloss_map(input)
    target = get_target(heatloss)
    algo = DijkstraAlgorithm(heatloss, continue_path_part1, partial(check_target_part1, target))
    return algo.run_algorithm()


def resolve_part2(input):
    heatloss = parse_heatloss_map(input)
    target = get_target(heatloss)
    algo = DijkstraAlgorithm(heatloss, continue_path_part2, partial(check_target_part2, target))
    return algo.run_algorithm()