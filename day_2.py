import re
from typing import NamedTuple, List
import itertools


GAME_REGEX = re.compile(r'Game (\d+): (.*)')


class Reveal(NamedTuple):
    blue: int
    green: int
    red: int


class Game(NamedTuple):
    id: int
    reveals: List[Reveal]


def parse_game(line: str) -> Game:
    game_match = GAME_REGEX.fullmatch(line)
    result = Game(int(game_match.group(1)), [])
    reveals_str = game_match.group(2).split(';')
    for reveal in reveals_str:
        blue_match = re.search(r'(\d+) blue', reveal)
        blues = int(blue_match.group(1)) if blue_match is not None else 0
        green_match = re.search(r'(\d+) green', reveal)
        greens = int(green_match.group(1)) if green_match is not None else 0
        red_match = re.search(r'(\d+) red', reveal)
        reds = int(red_match.group(1)) if red_match is not None else 0
        result.reveals.append(Reveal(blues, greens, reds))
    return result


def is_game_impossible(game: Game) -> bool:
    return any(r.red > 12 or r.green > 13 or r.blue > 14 for r in game.reveals)


def calculate_power_set(game: Game) -> int:
    blues = max(r.blue for r in game.reveals)
    greens = max(r.green for r in game.reveals)
    reds = max(r.red for r in game.reveals)
    return blues * greens * reds


def resolve_part1(input):
    possible_games = itertools.filterfalse(is_game_impossible, map(parse_game, input))
    return sum(game.id for game in possible_games)


def resolve_part2(input):
    return sum(map(calculate_power_set, map(parse_game, input)))