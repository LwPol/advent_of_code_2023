from typing import NamedTuple, Tuple, Union, Dict, List, Optional
import re
import itertools
from functools import partial


class Part(NamedTuple):
    x: int
    m: int
    a: int
    s: int

Range = Tuple[int, int]

class PartRange(NamedTuple):
    x: Range
    m: Range
    a: Range
    s: Range


class CompareInstruction(NamedTuple):
    category: str
    op: str
    limit: int
    destination: str

Instruction = Union[CompareInstruction, str]


def parse_instruction(ins_str: str) -> Instruction:
    m = re.match(r'([xmas])([<>])(\d+):(\w+)', ins_str)
    if m is not None:
        cat, op, limit, dest = m.groups()
        return CompareInstruction(cat, op, int(limit), dest)
    return ins_str


def parse_input(lines: List[str]) -> Tuple[Dict[str, List[Instruction]], List[Part]]:
    workflow_regex = re.compile(r'(\w+)\{(.+)\}')
    part_regex = re.compile(r'\{x=(\d+),m=(\d+),a=(\d+),s=(\d+)\}')
    def parse_workflow(line: str) -> Tuple[str, List[Instruction]]:
        match = workflow_regex.match(line)
        name, ins = match.groups()
        return name, [parse_instruction(token) for token in ins.split(',')]
    def parse_part(line: str) -> Part:
        match = part_regex.match(line)
        return Part(*map(int, match.groups()))
    gs = [list(g) for k, g in itertools.groupby(lines, key=bool) if k]
    return dict(map(parse_workflow, gs[0])), list(map(parse_part, gs[1]))


def process_workflow(workflow: List[Instruction], part: Part) -> str:
    for ins in workflow:
        if isinstance(ins, CompareInstruction):
            if ins.op == '<' and getattr(part, ins.category) < ins.limit:
                return ins.destination
            if ins.op == '>' and getattr(part, ins.category) > ins.limit:
                return ins.destination
        else:
            return ins


def is_part_accepted(workflows: Dict[str, List[Instruction]],
                     part: Part) -> bool:
    workflow = workflows['in']
    while workflow != 'A' and workflow != 'R':
        dest = process_workflow(workflow, part)
        if dest in workflows:
            workflow = workflows[dest]
        else:
            workflow = dest
    return workflow == 'A'


def sum_ratings(workflows: Dict[str, List[Instruction]], parts: List[Part]) -> int:
    accepted = filter(partial(is_part_accepted, workflows), parts)
    return sum(sum(part) for part in accepted)


def intersect_ranges(range1: Range, range2: Range) -> Optional[Range]:
    begin = max(range1[0], range2[0])
    end = min(range1[1], range2[1])
    if begin > end:
        return None
    return begin, end


def split_range(instruction: CompareInstruction,
                part_range: PartRange) -> Tuple[Optional[Range], Optional[Range]]:
    relevant = getattr(part_range, instruction.category)
    if instruction.op == '<':
        matching = intersect_ranges(relevant, (1, instruction.limit - 1))
        if matching is None:
            return None, part_range
        if matching[1] == relevant[1]:
            return part_range, None
        non_matching = (instruction.limit, relevant[1])
        return (part_range._replace(**{instruction.category: matching}),
                part_range._replace(**{instruction.category: non_matching}))
    if instruction.op == '>':
        matching = intersect_ranges(relevant, (instruction.limit + 1, 4000))
        if matching is None:
            return None, part_range
        if matching[0] == relevant[0]:
            return part_range, None
        non_matching = (relevant[0], instruction.limit)
        return (part_range._replace(**{instruction.category: matching}),
                part_range._replace(**{instruction.category: non_matching}))


def get_range_size(r: Range) -> int:
    return r[1] - r[0] + 1


def count_accepted(workflows: Dict[str, List[Instruction]],
                   current: str,
                   part_range: PartRange) -> int:
    if current == 'A':
        return (get_range_size(part_range.x) *
                get_range_size(part_range.m) *
                get_range_size(part_range.a) *
                get_range_size(part_range.s))
    if current == 'R':
        return 0

    result = 0
    workflow = workflows[current]
    for ins in workflow:
        if isinstance(ins, CompareInstruction):
            match, no_match = split_range(ins, part_range)
            if match is None:
                continue
            if no_match is None:
                return count_accepted(workflows, ins.destination, part_range)
            result += count_accepted(workflows, ins.destination, match)
            part_range = no_match
        else:
            result += count_accepted(workflows, ins, part_range)
    return result


def resolve_part1(input):
    return sum_ratings(*parse_input(input))


def resolve_part2(input):
    workflows, _ = parse_input(input)
    start = (1, 4000)
    return count_accepted(workflows, 'in', PartRange(start, start, start, start))
