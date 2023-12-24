from typing import NamedTuple, List, Tuple, Optional
import re
import itertools
import numpy as np


class Vector(NamedTuple):
    x: int
    y: int
    z: int

class Hailstone(NamedTuple):
    position: Vector
    velocity: Vector

Point6D = Tuple[float, float, float, float, float, float]


def parse_hailstones(lines: List[str]) -> List[Hailstone]:
    def parse_one(line: str) -> Hailstone:
        m = re.fullmatch(r'(\d+), (\d+), (\d+) @\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)', line)
        nums = map(int, m.groups())
        x, y, z, vx, vy, vz = nums
        return Hailstone(position=Vector(x, y, z), velocity=Vector(vx, vy, vz))
    return list(map(parse_one, lines))


def determinant(matrix_cols: List[List[int]]) -> int:
    return matrix_cols[0][0] * matrix_cols[1][1] - matrix_cols[0][1] * matrix_cols[1][0]


def calc_linear_coeffs(hailstone: Hailstone) -> Tuple[float, float]:
    col_a = [hailstone.position.x, hailstone.position.x + hailstone.velocity.x]
    col_b = [1, 1]
    col_y = [hailstone.position.y, hailstone.position.y + hailstone.velocity.y]
    main = determinant([col_a, col_b])
    a = determinant([col_y, col_b]) / main
    b = determinant([col_a, col_y]) / main 
    return a, b


def calc_paths_intersection(lhs: Hailstone, rhs: Hailstone) -> Optional[Tuple[float, float]]:
    a1, b1 = calc_linear_coeffs(lhs)
    a2, b2 = calc_linear_coeffs(rhs)
    if a1 == a2:
        return None
    
    x0 = (b2 - b1) / (a1 - a2)
    y0 = a1 * x0 + b1

    if (x0 - lhs.position.x) / lhs.velocity.x < 0:
        return None
    if (x0 - rhs.position.x) / rhs.velocity.x < 0:
        return None
    return x0, y0


def check_xy_intersection(lhs: Hailstone,
                          rhs: Hailstone,
                          min_bound: int,
                          max_bound: int) -> bool:
    collision = calc_paths_intersection(lhs, rhs)
    return (collision is not None and
            collision[0] >= min_bound and collision[0] <= max_bound and
            collision[1] >= min_bound and collision[1] <= max_bound)


def count_intersecting_paths(hailstones: List[Hailstone],
                             min_bound: int,
                             max_bound: int) -> int:
    return sum(1 for l, h in itertools.combinations(hailstones, 2)
               if check_xy_intersection(l, h, min_bound, max_bound))


# given 3 hailstone trajectories one can find solution to part 2 by solving following equation system
# with 6 variables: x, y, z, vx, vy, vz
# (vx - h1.vx)(h1.y - y) - (h1.x - x)(vy - h1.vy) = 0
# (vx - h1.vx)(h1.z - z) - (h1.x - x)(vz - h1.vz) = 0
# (vx - h2.vx)(h2.y - y) - (h2.x - x)(vy - h2.vy) = 0
# (vx - h2.vx)(h2.z - z) - (h2.x - x)(vz - h2.vz) = 0
# (vx - h3.vx)(h3.y - y) - (h3.x - x)(vy - h3.vy) = 0
# (vx - h3.vx)(h3.z - z) - (h3.x - x)(vz - h3.vz) = 0
# Since it's hard to solve analytically Newton's method can be used to find approximate solutions

def f(h1: Hailstone, h2: Hailstone, h3: Hailstone, arg: Point6D) -> Point6D:
    x, y, z, vx, vy, vz = arg
    return (
        (vx - h1.velocity.x) * (h1.position.y - y) - (h1.position.x - x) * (vy - h1.velocity.y),
        (vx - h1.velocity.x) * (h1.position.z - z) - (h1.position.x - x) * (vz - h1.velocity.z),
        (vx - h2.velocity.x) * (h2.position.y - y) - (h2.position.x - x) * (vy - h2.velocity.y),
        (vx - h2.velocity.x) * (h2.position.z - z) - (h2.position.x - x) * (vz - h2.velocity.z),
        (vx - h3.velocity.x) * (h3.position.y - y) - (h3.position.x - x) * (vy - h3.velocity.y),
        (vx - h3.velocity.x) * (h3.position.z - z) - (h3.position.x - x) * (vz - h3.velocity.z)
    )


def jacobian(h1: Hailstone, h2: Hailstone, h3: Hailstone, arg: Point6D) -> List[List[float]]:
    x, y, z, vx, vy, vz = arg
    return [
        [vy - h1.velocity.y, h1.velocity.x - vx,
         0, h1.position.y - y,
         x - h1.position.x, 0],
        [vz - h1.velocity.z, 0,
         h1.velocity.x - vx, h1.position.z - z,
         0, x - h1.position.x],
        [vy - h2.velocity.y, h2.velocity.x - vx,
         0, h2.position.y - y,
         x - h2.position.x, 0],
        [vz - h2.velocity.z, 0,
         h2.velocity.x - vx, h2.position.z - z,
         0, x - h2.position.x],
        [vy - h3.velocity.y, h3.velocity.x - vx,
         0, h3.position.y - y,
         x - h3.position.x, 0],
        [vz - h3.velocity.z, 0, h3.velocity.x - vx,
         h3.position.z - z, 0,
         x - h3.position.x]
    ]


def newton_method(h1: Hailstone, h2: Hailstone, h3: Hailstone, arg: Point6D) -> Point6D:
    xn = np.array([list(arg)]).transpose()
    fn = np.array([f(h1, h2, h3, arg)]).transpose()
    inv_j = np.linalg.inv(np.array(jacobian(h1, h2, h3, arg)))
    val = xn - inv_j.dot(fn)
    return tuple(list(val.transpose())[0])


def try_hailstones(h1: Hailstone, h2: Hailstone, h3: Hailstone):
    value = (200000000000000, 200000000000000, 200000000000000,
             0, 0, 0)
    for _ in range(15):
        value = newton_method(h1, h2, h3, value)
    
    rounded = tuple(round(n) for n in value)
    if f(h1, h2, h3, rounded) == (0, 0, 0, 0, 0, 0):
        return rounded

    
def check_solution_on_all_hailstones(hailstones: List[Hailstone], arg: Point6D) -> bool:
    x, y, z, vx, vy, vz = arg
    def check_one(h: Hailstone) -> bool:
        return (
            (vx - h.velocity.x) * (h.position.y - y) == (h.position.x - x) * (vy - h.velocity.y) and
            (vx - h.velocity.x) * (h.position.z - z) == (h.position.x - x) * (vz - h.velocity.z) and
            (h.position.x - x) * (vx - h.velocity.x) > 0
        )
    return all(check_one(h) for h in hailstones)


def find_rock_throw_position(hailstones: List[Hailstone]) -> Tuple[int, int, int]:
    for h1, h2, h3 in itertools.combinations(hailstones, 3):
        pos = try_hailstones(h1, h2, h3)
        if pos is not None and check_solution_on_all_hailstones(hailstones, pos):
            return pos[0], pos[1], pos[2]


def resolve_part1(input):
    hailstones = parse_hailstones(input)
    return count_intersecting_paths(hailstones,
                                    min_bound=200000000000000,
                                    max_bound=400000000000000)


def resolve_part2(input):
    return sum(find_rock_throw_position(parse_hailstones(input)))