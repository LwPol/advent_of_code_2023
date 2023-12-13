from typing import List, NamedTuple, Optional
import itertools


class Pattern(NamedTuple):
    grid: List[str]
    width: int
    height: int


def parse_patterns(lines: List[str]) -> List[Pattern]:
    def parse_one(pattern_str: List[str]) -> Pattern:
        return Pattern(grid=pattern_str, width=len(pattern_str[0]), height=len(pattern_str))
    grouped = itertools.groupby(lines, key=bool)
    return [parse_one(list(g)) for k, g in grouped if k]


def is_reflection_at_pos(pattern: Pattern, pos: int) -> bool:
    return all(pattern.grid[i] == pattern.grid[j]
               for i, j
               in zip(range(pos, -1, -1), range(pos + 1, pattern.height)))


def find_horizontal_reflection(pattern: Pattern) -> Optional[int]:
    for y in range(pattern.height - 1):
        if is_reflection_at_pos(pattern, y):
            return y
    return None


def transpose(pattern: Pattern) -> Pattern:
    transposed = Pattern(grid=list(itertools.repeat('', pattern.width)),
                         width=pattern.height,
                         height=pattern.width)
    for i in range(pattern.height):
        for j in range(pattern.width):
            transposed.grid[j] += pattern.grid[i][j]
    return transposed


def find_vertical_reflection(pattern: Pattern) -> Optional[int]:
    return find_horizontal_reflection(transpose(pattern))


def score_pattern(pattern: Pattern) -> int:
    horizontal = find_horizontal_reflection(pattern)
    if horizontal is not None:
        return 100 * (horizontal + 1)
    vertical = find_vertical_reflection(pattern)
    if vertical is not None:
        return vertical + 1
    raise RuntimeError('No mirror')


def check_rows_one_sign_difference(pattern: Pattern,
                                   idx1: int,
                                   idx2: int) -> Optional[int]:
    diffs = {i for i in range(pattern.width)
             if pattern.grid[idx1][i] != pattern.grid[idx2][i]}
    return next(iter(diffs)) if len(diffs) == 1 else None


def reverse_at(row: str, idx: int) -> str:
    return row[:idx] + ('#' if row[idx] == '.' else '.') + row[idx + 1:]


def find_smudged_reflection_horizontally(pattern: Pattern) -> Optional[int]:
    for x, y in itertools.combinations(range(pattern.height), r=2):
        if abs(x - y) % 2 == 1:
            smudge = check_rows_one_sign_difference(pattern, x, y)
            if smudge is not None:
                pattern.grid[x] = reverse_at(pattern.grid[x], smudge)
                found = is_reflection_at_pos(pattern, (x + y) // 2)
                pattern.grid[x] = reverse_at(pattern.grid[x], smudge)

                if found:
                    return (x + y) // 2


def find_smudged_reflection_vertically(pattern: Pattern) -> Optional[int]:
    return find_smudged_reflection_horizontally(transpose(pattern))


def score_smudged_pattern(pattern: Pattern) -> Optional[int]:
    horizontal = find_smudged_reflection_horizontally(pattern)
    if horizontal is not None:
        return 100 * (horizontal + 1)
    vertical = find_smudged_reflection_vertically(pattern)
    if vertical is not None:
        return vertical + 1
    raise RuntimeError('No smudge found')


def resolve_part1(input):
    return sum(score_pattern(p) for p in parse_patterns(input))


def resolve_part2(input):
    return sum(score_smudged_pattern(p) for p in parse_patterns(input))