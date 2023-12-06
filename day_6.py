import re
from typing import NamedTuple, List
import math
import functools


class Race(NamedTuple):
    time: int
    record: int


def parse_races(lines: List[str]) -> List[Race]:
    times = map(int, re.findall(r'\d+', lines[0]))
    dists = map(int, re.findall(r'\d+', lines[1]))
    return [Race(t, d) for t, d in zip(times, dists)]


def parse_entire_race(lines: List[str]) -> Race:
    time = int(lines[0].replace('Time:', '').replace(' ', ''))
    record = int(lines[1].replace('Distance:', '').replace(' ', ''))
    return Race(time, record)


def calculate_distance(total_time: int, time_to_hold: int) -> int:
    return time_to_hold * (total_time - time_to_hold)


def count_ways_to_win(race: Race):
    return sum(1 for i in range(1, race.time) if calculate_distance(race.time, i) > race.record)


def count_ways_to_win_part2(race: Race):
    delta = race.time ** 2 - 4 * race.record
    n1 = (race.time - math.sqrt(delta)) / 2
    begin = math.ceil(n1) if math.ceil(n1) != n1 else math.ceil(n1) + 1
    n2 = (race.time + math.sqrt(delta)) / 2
    end = math.floor(n2) if math.floor(n2) != n2 else math.floor(n2) - 1
    return end - begin + 1


def resolve_part1(input):
    races = parse_races(input)
    return functools.reduce(lambda x, y: x * y, map(count_ways_to_win, races), 1)


def resolve_part2(input):
    return count_ways_to_win_part2(parse_entire_race(input))