from typing import List, Tuple, Set, NamedTuple
import itertools


Position = Tuple[int, int]


def expand_columns(grid: List[str]) -> None:
    i = 0
    while i < len(grid[0]):
        if all(grid[j][i] == '.' for j in range(len(grid))):
            for each in range(len(grid)):
                grid[each] = grid[each][:i] + '.' + grid[each][i:]
            i += 1
        i += 1


def expand_rows(grid: List[str]) -> None:
    i = 0
    width = len(grid[0])
    while i < len(grid):
        if all(c == '.' for c in grid[i]):
            grid.insert(i, ''.join(itertools.repeat('.', width)))
            i += 1
        i += 1


def find_galaxies(grid: List[str]) -> Set[Position]:
    galaxies = set()
    for i, j in itertools.product(range(len(grid[0])), range(len(grid))):
        if grid[j][i] == '#':
            galaxies.add((i, j))
    return galaxies


def sum_shortest_paths(galaxies: Set[Position]) -> int:
    return sum(abs(g2[0] - g1[0]) + abs(g2[1] - g1[1]) for g1, g2 in itertools.combinations(galaxies, r=2))


def find_vertical_empty_spaces(grid: List[str]) -> List[int]:
    result: List[int] = []
    for idx, _ in enumerate(grid[0]):
        if all(grid[y][idx] == '.' for y in range(len(grid))):
            result.append(idx)
    return result


def find_horizontal_empty_spaces(grid: List[str]) -> List[int]:
    result: List[int] = []
    for idx, row in enumerate(grid):
        if all(c == '.' for c in row):
            result.append(idx)
    return result


def sum_shortest_paths_after_expansion(grid: List[str], expansion_size: int) -> int:
    vertical_spaces = find_vertical_empty_spaces(grid)
    horizontal_spaces = find_horizontal_empty_spaces(grid)
    galaxies = find_galaxies(grid)
    def count_distance(g1: Position, g2: Position) -> int:
        dist = abs(g2[0] - g1[0]) + abs(g2[1] - g1[1])
        x_sorted = sorted((g1[0], g2[0]))
        y_sorted = sorted((g1[1], g2[1]))

        for space in vertical_spaces:
            if x_sorted[0] < space < x_sorted[1]:
                dist += (expansion_size - 1)
        for space in horizontal_spaces:
            if y_sorted[0] < space < y_sorted[1]:
                dist += (expansion_size - 1)
        return dist
    return sum(count_distance(g1, g2) for g1, g2 in itertools.combinations(galaxies, r=2))


def resolve_part1(input):
    grid = input[:]
    expand_columns(grid)
    expand_rows(grid)
    return sum_shortest_paths(find_galaxies(grid))


def resolve_part2(input):
    return sum_shortest_paths_after_expansion(input, expansion_size=1000000)