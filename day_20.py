from typing import NamedTuple, Dict, Tuple, Union, List, Optional
from queue import Queue
from dataclasses import dataclass


@dataclass
class FlipFlop:
    on: bool


@dataclass
class Conjunction:
    inputs: Dict[str, bool]


class Signal(NamedTuple):
    source: str
    value: bool
    destination: str

ConfigItem = Tuple[Optional[Union[FlipFlop, Conjunction]], List[str]]
Configuration = Dict[str, ConfigItem]


def parse_config(lines: List[str]) -> Dict[str, ConfigItem]:
    def parse_one(line: str) -> Tuple[str, ConfigItem]:
        name, rest = line.split(' -> ')
        destinations = rest.split(', ')
        if name.startswith('%'):
            return name[1:], (FlipFlop(False), destinations)
        if name.startswith('&'):
            return name[1:], (Conjunction({}), destinations)
        return name, (None, destinations)
    result = dict(map(parse_one, lines))
    testing_outputs = set()
    for module, item in result.items():
        for dest in item[1]:
            if dest not in result:
                testing_outputs.add(dest)
            elif isinstance(result[dest][0], Conjunction):
                result[dest][0].inputs[module] = False
    for dummy in testing_outputs:
        result[dummy] = (None, [])
    return result


def push_button(configuration: Configuration) -> Tuple[int, int]:
    signals = Queue()
    signals.put(Signal('', False, 'broadcaster'))
    low, high = 0, 0
    while not signals.empty():
        src, value, current = signals.get()
        if value:
            high += 1
        else:
            low += 1
        state, destinations = configuration[current]
        if isinstance(state, FlipFlop):
            if not value:
                state.on = not state.on
                for dest in destinations:
                    signals.put(Signal(current, state.on, dest))
        elif isinstance(state, Conjunction):
            state.inputs[src] = value
            new_pulse = not all(state.inputs.values())
            for dest in destinations:
                signals.put(Signal(current, new_pulse, dest))
        elif current == 'broadcaster':
            for dest in destinations:
                signals.put(Signal(current, value, dest))
    return low, high


def keep_pushing_button(config: Configuration, times: int) -> int:
    low, high = 0, 0
    for _ in range(times):
        l, h = push_button(config)
        low += l
        high += h
    return low * high


def resolve_part1(input):
    return keep_pushing_button(parse_config(input), 1000)


def resolve_part2(input):
    return """
Solved manually. 'rx' node is connected to a single conjecture node that will send
low signal iff all its inputs are high. After adding monitoring for inputs of node connected to 'rx'
i.e. 'zg' one might notice that each part of input procudes high signals every n button clicks.
LCM of ns for each input module gives good guess where high signals line up and produce result
"""