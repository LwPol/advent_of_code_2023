import re
from typing import NamedTuple, Dict, Tuple, List
import itertools
import math
import functools


class Network(NamedTuple):
    instructions: str
    nodes: Dict[str, Tuple[str, str]]


class PathCycle(NamedTuple):
    start: int
    length: int
    zs_before_cycle: List[int]
    zs_in_cycle: List[int]


def parse_network(lines: List[str]) -> Network:
    def parse_connection(line: str) -> Tuple[str, str, str]:
        m = re.match(r'(\w+) = \((\w+), (\w+)\)', line)
        return m.groups()
    ins = lines[0]
    conns = {node: (left, right) for node, left, right in map(parse_connection, lines[2:])}
    return Network(instructions=ins, nodes=conns)


def count_steps_to_zzz(network: Network) -> int:
    dirs = itertools.cycle(network.instructions)
    current = 'AAA'
    steps = 0
    while current != 'ZZZ':
        next_dir = next(dirs)
        conns = network.nodes[current]
        current = conns[0 if next_dir == 'L' else 1]
        steps += 1
    return steps


class Simulation:
    def __init__(self, network: Network, start: str):
        self.__network = network
        self.__dirs = itertools.cycle(enumerate(network.instructions))
        self.next_dir = next(self.__dirs)
        self.current_pos = start
    
    def advance_pos(self):
        idx, next_dir = self.next_dir
        self.next_dir = next(self.__dirs)
        self.last_dir_idx = idx
        self.current_pos = self.__network.nodes[self.current_pos][0 if next_dir == 'L' else 1]
        return self
    
    def descriptor(self):
        return (self.next_dir[0], self.current_pos)
    
    def __eq__(self, other: "Simulation") -> bool:
        return self.descriptor() == other.descriptor()


def tortoise_and_hare(network: Network, start: str) -> Tuple[int, int]:
    tortoise = Simulation(network, start).advance_pos()
    hare = Simulation(network, start).advance_pos().advance_pos()
    while tortoise != hare:
        tortoise.advance_pos()
        hare.advance_pos().advance_pos()
    
    mu = 0
    tortoise = Simulation(network, start)
    while tortoise != hare:
        tortoise.advance_pos()
        hare.advance_pos()
        mu += 1
    
    lam = 1
    begin = tortoise.descriptor()
    hare = tortoise.advance_pos()
    while begin != hare.descriptor():
        hare.advance_pos()
        lam += 1
    return mu, lam


def find_cycle_in_path(network: Network, start: str) -> PathCycle:
    mu, lam = tortoise_and_hare(network, start)
    zs_before = []

    s = Simulation(network, start)
    for idx in range(mu):
        if s.current_pos[-1] == 'Z':
            zs_before.append(idx)
        s.advance_pos()
    
    idx = mu
    zs_after = []
    for _ in range(lam):
        if s.current_pos[-1] == 'Z':
            zs_after.append(idx)
        idx += 1
        s.advance_pos()
    return PathCycle(mu, lam, zs_before, zs_after)


# it seems that real input data has the following properties:
# 1. no path encounters ??Z before start of the cycle
# 2. each path encounters ??Z exactly once in the cycle
# 3. number of steps to reach ??Z is equal to length of the cycle
# if all predicates above are satisfied then getting answer is simply
# calculating lcm of lengths of the cycles
def is_lcm_viable_solution(cycles: List[PathCycle]) -> bool:
    return all(not c.zs_before_cycle and len(c.zs_in_cycle) == 1 and c.zs_in_cycle[0] == c.length
               for c in cycles)


def lcm_impl(a: int, b: int) -> int:
    return a*b // math.gcd(a, b)


def lcm(*nums) -> int:
    return functools.reduce(lcm_impl, nums)


def solve_with_lcm(network: Network) -> int:
    starting_nodes = list(filter(lambda n: n[-1] == 'A', network.nodes.keys()))
    paths = [find_cycle_in_path(network, node) for node in starting_nodes]
    if not is_lcm_viable_solution(paths):
        raise Exception("Does not work for the general problem")
    return lcm(*(path.length for path in paths))


def resolve_part1(input):
    return count_steps_to_zzz(parse_network(input))


def resolve_part2(input):
    return solve_with_lcm(parse_network(input))
