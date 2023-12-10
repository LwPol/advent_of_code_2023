from typing import List, Iterator
import functools


def parse_values(lines: List[str]) -> List[List[int]]:
    def parse_one(line: str) -> List[int]:
        return list(map(int, line.split()))
    return [parse_one(l) for l in lines]


def generate_diff(values: List[int]) -> List[int]:
    return [y - x for x, y in zip(values, values[1:])]


def generate_diffs_last_numbers(values: List[int]) -> Iterator[int]:
    yield values[-1]
    if all(v == 0 for v in values):
        return
    diff = generate_diff(values)
    yield from generate_diffs_last_numbers(diff)


def generate_diffs_first_numbers(values: List[int]) -> Iterator[int]:
    yield values[0]
    if all(v == 0 for v in values):
        return
    diff = generate_diff(values)
    yield from generate_diffs_first_numbers(diff)


def extrapolate(values: List[int]) -> int:
    lasts = generate_diffs_last_numbers(values)
    return sum(lasts)


def extrapolate_beginnings(values: List[int]) -> int:
    firsts = reversed(list(generate_diffs_first_numbers(values)))
    return functools.reduce(lambda x, y: y - x, firsts)


def extrapolate_all(values: List[List[int]]) -> int:
    return sum(extrapolate(seq) for seq in values)


def extrapolate_all_beginnings(values: List[List[int]]) -> int:
    return sum(extrapolate_beginnings(seq) for seq in values)


def resolve_part1(input):
    return extrapolate_all(parse_values(input))


def resolve_part2(input):
    return extrapolate_all_beginnings(parse_values(input))