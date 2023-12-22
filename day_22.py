from typing import NamedTuple, Tuple, List, Optional, Dict, Set
from collections import defaultdict
import itertools
from queue import PriorityQueue
from functools import partial


Point = Tuple[int, int, int]
Range = Tuple[int, int]

class Brick(NamedTuple):
    begin: Point
    end: Point

LevelsMapping = Dict[int, List[Brick]]
LevelsMappings = Tuple[LevelsMapping, LevelsMapping]


def bottom(brick: Brick) -> int:
    return min(brick.begin[2], brick.end[2])


def top(brick: Brick) -> int:
    return max(brick.begin[2], brick.end[2])


def parse_bricks(lines: List[str]) -> List[Brick]:
    def parse_one(line: str) -> Brick:
        beg, end = line.split('~')
        return Brick(begin=tuple(int(c) for c in beg.split(',')),
                     end=tuple(int(c) for c in end.split(',')))
    return sorted(map(parse_one, lines), key=bottom)


def intersect_ranges(range1: Range, range2: Range) -> Optional[Range]:
    begin = max(range1[0], range2[0])
    end = min(range1[1], range2[1])
    if begin > end:
        return None
    return begin, end


def could_fall_on_each_other(lhs: Brick, rhs: Brick) -> bool:
    dx1 = tuple(sorted((lhs.begin[0], lhs.end[0])))
    dy1 = tuple(sorted((lhs.begin[1], lhs.end[1])))
    dx2 = tuple(sorted((rhs.begin[0], rhs.end[0])))
    dy2 = tuple(sorted((rhs.begin[1], rhs.end[1])))
    return (intersect_ranges(dx1, dx2) is not None and
            intersect_ranges(dy1, dy2) is not None)


def bring_brick_down(brick: Brick, dz: int) -> Brick:
    begin = (brick.begin[0], brick.begin[1], brick.begin[2] - dz)
    end = (brick.end[0], brick.end[1], brick.end[2] - dz)
    return Brick(begin, end)


def fall_brick(brick: Brick, fallen: List[Brick]) -> None:
    current_z = bottom(brick)
    for grounded in reversed(fallen):
        grounded_z = top(grounded)
        if grounded_z >= current_z:
            continue

        if could_fall_on_each_other(brick, grounded):
            fallen.append(bring_brick_down(brick, dz=current_z - grounded_z - 1))
            break
    else:
        fallen.append(bring_brick_down(brick, dz=current_z - 1))
    fallen.sort(key=top)


def fall_all_bricks(bricks: List[Brick]) -> List[Brick]:
    fallen: List[Brick] = []
    for brick in bricks:
        fall_brick(brick, fallen)
    return fallen


def map_bricks_per_level(fallen: List[Brick]) -> LevelsMappings:
    per_top, per_bottom = defaultdict(list), defaultdict(list)
    for brick in fallen:
        per_top[top(brick)].append(brick)
        per_bottom[bottom(brick)].append(brick)
    return per_top, per_bottom


def is_safe_to_remove(per_level: LevelsMappings, brick: Brick) -> bool:
    per_top, per_bottom = per_level
    z = top(brick)
    higher = per_bottom[z + 1]
    equal = [b for b in per_top[z] if b != brick]
    return all(any(could_fall_on_each_other(above, eq) for eq in equal) for above in higher)


def count_safe_bricks(per_level: LevelsMappings) -> int:
    bricks = itertools.chain.from_iterable(per_level[0].values())
    return sum(1 for brick in bricks if is_safe_to_remove(per_level, brick))


def destroy_brick(per_level: LevelsMappings, brick: Brick) -> Set[Brick]:
    per_top, per_bottom = per_level
    destroyed = {brick}
    queue = PriorityQueue()
    queue.put(top(brick))
    while not queue.empty():
        current_level = queue.get()
        for brick in per_bottom[current_level + 1]:
            if (brick not in destroyed and
                all(ground in destroyed or not could_fall_on_each_other(brick, ground)
                    for ground in per_top[current_level])):
                destroyed.add(brick)
                queue.put(top(brick))
    return destroyed


def sum_falling_bricks(fallen: List[Brick]) -> int:
    mappings = map_bricks_per_level(fallen)
    unsafe = itertools.filterfalse(partial(is_safe_to_remove, mappings), fallen)
    return sum(len(destroy_brick(mappings, brick)) - 1 for brick in unsafe)

def resolve_part1(input):
    fallen = fall_all_bricks(parse_bricks(input))
    per_level = map_bricks_per_level(fallen)
    return count_safe_bricks(per_level)


def resolve_part2(input):
    fallen = fall_all_bricks(parse_bricks(input))
    return sum_falling_bricks(fallen)