from typing import NamedTuple, List, Iterable, Tuple
import re
import itertools


class DigStep(NamedTuple):
    direction: str
    count: int
    color: str


def parse_dig_plan(lines: Iterable[str]) -> List[DigStep]:
    def parse_one(line: str) -> DigStep:
        m = re.match(r'(\w) (\d+) \(#([0-9a-f]+)\)', line)
        d, c, col = m.groups()
        return DigStep(direction=d, count=int(c), color=col)
    return list(map(parse_one, lines))


def convert_dig_plan(dig_plan: Iterable[DigStep]) -> List[DigStep]:
    dir_map = {'0': 'R', '1': 'D', '2': 'L', '3': 'U'}
    def convert_one(step: DigStep) -> DigStep:
        count = int(step.color[:5], 16)
        direction = dir_map[step.color[-1]]
        return DigStep(direction, count, color='')
    return list(map(convert_one, dig_plan))


def is_clockwise(points: List[Tuple[int, int]]) -> bool:
    edges = itertools.chain(zip(points, points[1:]), [(points[-1], points[0])])
    return sum((p2[0] - p1[0]) * (p2[1] + p1[1]) for p1, p2 in edges) < 0


def traverse_outline(dig_plan: Iterable[DigStep]) -> List[Tuple[int, int]]:
    current_point = (0, 0)
    points = []
    for step in dig_plan:
        x, y = current_point
        if step.direction == 'R':
            current_point = (x + step.count, y)
        elif step.direction == 'L':
            current_point = (x - step.count, y)
        elif step.direction == 'D':
            current_point = (x, y + step.count)
        elif step.direction == 'U':
            current_point = (x, y - step.count)
        points.append(current_point)
    if not is_clockwise(points):
        points.reverse()
    return points


def get_vertices(dig_plan: List[DigStep]) -> List[Tuple[int, int]]:
    points = traverse_outline(dig_plan)
    edges = list(itertools.chain(zip(points, points[1:]), [(points[-1], points[0])]))
    vertices = []
    for e1, e2 in itertools.chain(zip(edges, edges[1:]), [(edges[-1], edges[0])]):
        dx1 = e1[1][0] - e1[0][0]
        dy1 = e1[1][1] - e1[0][1]
        dx2 = e2[1][0] - e2[0][0]
        dy2 = e2[1][1] - e2[0][1]
        if dx1 > 0:
            if dy2 > 0:
                vertices.append((e1[1][0] + 1, e1[1][1]))
            else:
                vertices.append((e1[1][0], e1[1][1]))
        if dx1 < 0:
            if dy2 > 0:
                vertices.append((e1[1][0] + 1, e1[1][1] + 1))
            else:
                vertices.append((e1[1][0], e1[1][1] + 1))
        if dy1 > 0:
            if dx2 > 0:
                vertices.append((e1[1][0] + 1, e1[1][1]))
            else:
                vertices.append((e1[1][0] + 1, e1[1][1] + 1))
        if dy1 < 0:
            if dx2 > 0:
                vertices.append((e1[1][0], e1[1][1]))
            else:
                vertices.append((e1[1][0], e1[1][1] + 1))
    return vertices


def calculate_surface(vertices: List[Tuple[int, int]]) -> int:
    surface = 0
    for p1, p2 in itertools.chain(zip(vertices, vertices[1:]), [(vertices[-1], vertices[0])]):
        x1, y1 = p1
        x2, y2 = p2
        surface += x1 * y2 - x2 * y1
    return surface // 2


def resolve_part1(input):
    return calculate_surface(get_vertices(parse_dig_plan(input)))


def resolve_part2(input):
    return calculate_surface(get_vertices(convert_dig_plan(parse_dig_plan(input))))