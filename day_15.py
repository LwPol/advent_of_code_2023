from typing import List, Tuple
import functools
import re


def hash_string(value: str) -> int:
    def calc(acc: int, current: str) -> int:
        acc += ord(current)
        acc *= 17
        acc %= 256
        return acc
    return functools.reduce(calc, value, 0)


def parse_step(value: str) -> Tuple[str, str, int]:
    m = re.match(r'(\w+)(.)(\d*)', value)
    label = m.group(1)
    op = m.group(2)
    count = int(m.group(3)) if m.group(3) else 0
    return label, op, count


def run_initialisation_sequence(steps: List[str]) -> List[List[Tuple[str, int]]]:
    boxes: List[List[Tuple[str, int]]] = [[] for _ in range(256)]
    for step in steps:
        label, op, count = parse_step(step)
        hashed = hash_string(label)
        if op == '-':
            boxes[hashed] = list(filter(lambda x: x[0] != label, boxes[hashed]))
        if op == '=':
            for idx, elem in enumerate(boxes[hashed]):
                if elem[0] == label:
                    boxes[hashed][idx] = (label, count)
                    break
            else:
                boxes[hashed].append((label, count))
    return boxes


def calculate_focusing_power(boxes: List[Tuple[str, int]]) -> int:
    result = 0
    for idx, box in enumerate(boxes, start=1):
        for slot, elem in enumerate(box, start=1):
            result += idx * slot * elem[1]
    return result


def resolve_part1(input):
    return sum(map(hash_string, input[0].split(',')))


def resolve_part2(input):
    return calculate_focusing_power(run_initialisation_sequence(input[0].split(',')))