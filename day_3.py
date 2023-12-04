from typing import NamedTuple, List, Iterator, Tuple, Set, Optional
import itertools


class EngineSchematic(NamedTuple):
    schema: List[str]
    width: int
    height: int


def get_char_from_schematics(schematics: EngineSchematic, x: int, y: int) -> str:
    return schematics.schema[y][x]


def parse_engine_schematics(input: List[str]) -> EngineSchematic:
    return EngineSchematic(schema=input, width=len(input[0]), height=len(input))


def get_symbol_positions(schematics: EngineSchematic) -> Iterator[Tuple[int, int]]:
    for x, y in itertools.product(range(schematics.width), range(schematics.height)):
        char = get_char_from_schematics(schematics, x, y)
        if char != '.' and not char.isdigit():
            yield (x, y)


def get_gears_positions(schematics: EngineSchematic) -> Iterator[Tuple[int, int]]:
    return filter(lambda pos: get_char_from_schematics(schematics, *pos) == '*',
                  get_symbol_positions(schematics))


def get_positions_around_point(schematics: EngineSchematic,
                               position: Tuple[int, int]) -> List[Tuple[int, int]]:
    def is_in_bounds(pos: Tuple[int, int]) -> bool:
        return (pos[0] >= 0 and pos[0] < schematics.width and
                pos[1] >= 0 and pos[1] < schematics.height)
    directions = (
        (-1, -1), (0, -1), (1, -1), (1, 0),
        (1, 1), (0, 1), (-1, 1), (-1, 0)
    )
    neighbours = ((position[0] + dx, position[1] + dy) for dx, dy in directions)
    return list(filter(is_in_bounds, neighbours))


class PartNumbersParser:
    def __init__(self, schematics: EngineSchematic):
        self.__schema = schematics
        self.__numbers_bookeeping: Set[Tuple[int, int]] = set()
        self.__part_number_sum = 0
    
    def sum_part_numbers(self) -> int:
        for pos in get_symbol_positions(self.__schema):
            self.__mark_numbers_around_symbol(pos)
        return self.__part_number_sum
    
    def sum_gear_ratios(self) -> int:
        result = 0
        for pos in get_gears_positions(self.__schema):
            nums = self.__mark_numbers_around_symbol(pos)
            self.__numbers_bookeeping.clear()
            if len(nums) == 2:
                result += nums[0] * nums[1]
        return result
    
    def __mark_numbers_around_symbol(self, symbol_pos: Tuple[int, int]) -> List[int]:
        numbers = []
        for pos in get_positions_around_point(self.__schema, symbol_pos):
            if get_char_from_schematics(self.__schema, *pos).isdigit():
                result = self.__mark_number(pos)
                if result is not None:
                    numbers.append(result)
        return numbers
    
    def __mark_number(self, digit_pos: Tuple[int, int]) -> Optional[int]:
        x, y = digit_pos
        def digit_on_the_left(x_coord: int) -> Optional[int]:
            x_coord -= 1
            if x_coord >= 0 and get_char_from_schematics(self.__schema, x_coord, y).isdigit():
                return x_coord
        while (new_x := digit_on_the_left(x)) is not None:
            x = new_x
        
        if (x, y) in self.__numbers_bookeeping:
            return None
        
        self.__numbers_bookeeping.add((x, y))
        number = self.__get_number((x, y))
        self.__part_number_sum += number
        return number

    def __get_number(self, begin_pos: Tuple[int, int]) -> int:
        digits = []
        x, y = begin_pos
        while (x < self.__schema.width and
               (char := get_char_from_schematics(self.__schema, x, y)).isdigit()):
            digits.append(char)
            x += 1
        return int(''.join(digits))


def resolve_part1(input):
    parser = PartNumbersParser(parse_engine_schematics(input))
    return parser.sum_part_numbers()


def resolve_part2(input):
    parser = PartNumbersParser(parse_engine_schematics(input))
    return parser.sum_gear_ratios()