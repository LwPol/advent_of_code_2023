from typing import NamedTuple, Dict, Tuple, Set, List, Iterator
from collections import defaultdict
from queue import Queue


Point = Tuple[int, int]
Path = Tuple[Tuple[Point, Point], int]
Edge = Tuple[Point, int]

class HikingTrail(NamedTuple):
    terrain: Dict[Point, str]
    source: Point
    target: Point


def parse_trail(lines: List[str]) -> HikingTrail:
    terrain = {}
    for y, row in enumerate(lines):
        for x, elem in enumerate(row):
            terrain[(x, y)] = elem
    for x, elem in enumerate(lines[0]):
        if elem == '.':
            src = (x, 0)
            break
    for x, elem in enumerate(lines[-1]):
        if elem == '.':
            target = (x, len(lines) - 1)
            break
    return HikingTrail(terrain, src, target)


def continue_path(terrain: Dict[Point, str],
                  visited: Set[Point],
                  current: Point) -> Iterator[Point]:
    x, y = current
    cur = terrain[current]
    if cur == '>':
        dirs = [(1, 0)]
    elif cur == '<':
        dirs = [(-1, 0)]
    elif cur == '^':
        dirs = [(0, -1)]
    elif cur == 'v':
        dirs = [(0, 1)]
    else:
        dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))

    for dx, dy in dirs:
        next_pos = (x + dx, y + dy)
        if next_pos in terrain and next_pos not in visited and terrain[next_pos] != '#':
            yield next_pos


def find_longest_path(trail: HikingTrail,
                      start_pos: Point,
                      visited: Set[Point]) -> int:
    current = start_pos
    while current != trail.target:
        visited.add(current)
        candidates = list(continue_path(trail.terrain, visited, current))
        if len(candidates) == 1:
            current = candidates[0]
        else:
            longest = 0
            for pos in candidates:
                length = find_longest_path(trail, pos, visited.copy())
                longest = max(longest, length)
            return longest
    return len(visited)


def continue_path_ignore_slopes(terrain: Dict[Point, str],
                                visited: Set[Point],
                                current: Point) -> Iterator[Point]:
    x, y = current
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for dx, dy in dirs:
        next_pos = (x + dx, y + dy)
        if next_pos in terrain and next_pos not in visited and terrain[next_pos] != '#':
            yield next_pos


def goto_intersection_or_target(trail: HikingTrail,
                                starting_intersection: Point,
                                current: Point):
    visited = {starting_intersection}
    while len(candidates :=
              list(continue_path_ignore_slopes(trail.terrain, visited, current))) == 1:
        visited.add(current)
        current = candidates[0]
    return current, visited - {starting_intersection}


def collect_paths_impl(trail: HikingTrail,
                       first_crossroad: Point,
                       path_start: Point,
                       visited: Set[Point]) -> List[Path]:
    crossroad, newly_visited = goto_intersection_or_target(trail, first_crossroad, path_start)
    visited.update(newly_visited)
    paths: List[Path] = [((first_crossroad, crossroad), len(newly_visited) + 1)]
    for tile in continue_path_ignore_slopes(trail.terrain, visited, crossroad):
        paths.extend(collect_paths_impl(trail, crossroad, tile, visited))
    return paths


def collect_paths(trail: HikingTrail) -> List[Path]:
    return collect_paths_impl(trail, trail.source, trail.source, set())


def build_graph(paths: List[Path]) -> Dict[Point, Edge]:
    result = defaultdict(list)
    for edge, weight in paths:
        p1, p2 = edge
        result[p1].append((p2, weight))
        result[p2].append((p1, weight))
    return result


def bfs(graph: Dict[Point, Edge], starting_pos: Point) -> Dict[int, List[Point]]:
    leveled = defaultdict(list)
    queue = Queue()
    queue.put((starting_pos, 0))
    visited = set()
    while not queue.empty():
        node, lvl = queue.get()
        if node in visited:
            continue
        visited.add(node)
        leveled[lvl].append(node)
        
        for connected, _ in graph[node]:
            queue.put((connected, lvl + 1))
    return leveled


def find_longest_path_ignore_slopes_impl(graph: Dict[Point, Edge],
                                         levels: Dict[int, List[Point]],
                                         start_node: Point,
                                         cur_level: int,
                                         target_node: Point,
                                         visited: Set[Point]) -> int:
    if start_node == target_node:
        return 0

    visited.add(start_node)
    longest = -1
    for node, weight in graph[start_node]:
        if node in visited:
            continue
        is_prev_level = node in levels[cur_level - 1]
        if is_prev_level and all(n in visited for n in levels[cur_level]):
            continue
        if is_prev_level:
            lvl = cur_level - 1
        elif node in levels[cur_level]:
            lvl = cur_level
        else:
            lvl = cur_level + 1
        length = find_longest_path_ignore_slopes_impl(
            graph, levels, node, lvl, target_node, visited.copy()
        )
        if length is not None:
            longest = max(longest, length + weight)
    return longest if longest != -1 else None


def find_longest_path_ignore_slopes(trail: HikingTrail) -> int:
    paths = collect_paths(trail)
    graph = build_graph(paths)
    levels = bfs(graph, trail.source)
    return find_longest_path_ignore_slopes_impl(
        graph, levels, trail.source, 0, trail.target, visited=set())


def resolve_part1(input):
    trail = parse_trail(input)
    return find_longest_path(trail, trail.source, set())


def resolve_part2(input):
    return find_longest_path_ignore_slopes(parse_trail(input))