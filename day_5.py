import re
from typing import NamedTuple, List, Iterable, Iterator, Tuple, Optional
import math
import itertools


class MappingRange(NamedTuple):
    source_begin: int
    dest_begin: int
    count: int


class Interval(NamedTuple):
    begin: int
    end: int


class Almanac(NamedTuple):
    soil_map: List[MappingRange]
    fertilizer_map: List[MappingRange]
    water_map: List[MappingRange]
    light_map: List[MappingRange]
    temperature_map: List[MappingRange]
    humidity_map: List[MappingRange]
    location_map: List[MappingRange]


def parse_almanac(lines: List[str]) -> Tuple[Almanac, List[int]]:
    def parse_range(line: str) -> MappingRange:
        m = re.match(r'(\d+) (\d+) (\d+)', line)
        return MappingRange(source_begin=int(m.group(2)),
                            dest_begin=int(m.group(1)),
                            count=int(m.group(3)))
    def find_line(pattern: str) -> int:
        return next(idx for idx, line in enumerate(lines) if line == pattern)
    def parse_range_list(start_idx: int) -> List[MappingRange]:
        result: List[MappingRange] = []
        idx = start_idx
        while idx < len(lines) and lines[idx]:
            result.append(parse_range(lines[idx]))
            idx += 1
        result.sort(key=lambda mr: mr.source_begin)
        return result
    
    return Almanac(
        soil_map=parse_range_list(find_line('seed-to-soil map:') + 1),
        fertilizer_map=parse_range_list(find_line('soil-to-fertilizer map:') + 1),
        water_map=parse_range_list(find_line('fertilizer-to-water map:') + 1),
        light_map=parse_range_list(find_line('water-to-light map:') + 1),
        temperature_map=parse_range_list(find_line('light-to-temperature map:') + 1),
        humidity_map=parse_range_list(find_line('temperature-to-humidity map:') + 1),
        location_map=parse_range_list(find_line('humidity-to-location map:') + 1)
    ), [int(num) for num in re.findall(r'\d+', lines[0])]


def build_seed_intervals(seeds: List[int]) -> List[Interval]:
    return [Interval(begin, begin + count - 1)
            for begin, count in zip(seeds[0::2], seeds[1::2])]


def map_seed_to_location(almanac: Almanac, seed: int) -> int:
    def map_value(src: int, ranges: Iterable[MappingRange]) -> int:
        for r in ranges:
            if r.source_begin <= src < r.source_begin + r.count:
                return r.dest_begin + src - r.source_begin
        return src
    soil = map_value(seed, almanac.soil_map)
    fertilizer = map_value(soil, almanac.fertilizer_map)
    water = map_value(fertilizer, almanac.water_map)
    light = map_value(water, almanac.light_map)
    temperature = map_value(light, almanac.temperature_map)
    humidity = map_value(temperature, almanac.humidity_map)
    return map_value(humidity, almanac.location_map)


def intersect_intervals(lhs: Interval, rhs: Interval) -> Optional[Interval]:
    begin = max(lhs.begin, rhs.begin)
    end = min(lhs.end, rhs.end)
    if begin > end:
        return None
    return Interval(begin, end)


def map_intervals(values_range: Interval,
                  mappings: List[MappingRange]) -> List[Interval]:
    def generate_mapping_intervals() -> Iterator[Tuple[Interval, Optional[MappingRange]]]:
        yield Interval(begin=-math.inf, end=mappings[0].source_begin - 1), None
        for r1, r2 in zip(mappings, mappings[1:]):
            yield Interval(r1.source_begin, r1.source_begin + r1.count - 1), r1
            if r2.source_begin != r1.source_begin + r1.count:
                yield Interval(r1.source_begin + r1.count, r2.source_begin - 1), None
        
        last = mappings[-1]
        yield Interval(last.source_begin, last.source_begin + last.count - 1), last
        yield Interval(begin=last.source_begin + last.count, end=math.inf), None
    
    result: List[Interval] = []
    for range_interval, mapping in generate_mapping_intervals():
        if values_range.begin > range_interval.end:
            continue
        if values_range.end < range_interval.begin:
            break
        intersection = intersect_intervals(values_range, range_interval)
        if mapping is None:
            result.append(intersection)
        else:
            offset = intersection.begin - mapping.source_begin
            last_offset = offset + intersection.end - intersection.begin
            result.append(Interval(begin=mapping.dest_begin + offset,
                                   end=mapping.dest_begin + last_offset))
    return result


def map_seed_range(seed_range: Interval, almanac: Almanac) -> List[Interval]:
    soils = map_intervals(seed_range, almanac.soil_map)
    fertilizers = list(
        itertools.chain.from_iterable(map_intervals(sr, almanac.fertilizer_map)
                                      for sr in soils)
    )
    waters = list(
        itertools.chain.from_iterable(map_intervals(fr, almanac.water_map)
                                      for fr in fertilizers)
    )
    lights = list(
        itertools.chain.from_iterable(map_intervals(wr, almanac.light_map)
                                      for wr in waters)
    )
    temperatures = list(
        itertools.chain.from_iterable(map_intervals(lr, almanac.temperature_map)
                                      for lr in lights)
    )
    humiditys = list(
        itertools.chain.from_iterable(map_intervals(tr, almanac.humidity_map)
                                      for tr in temperatures)
    )
    locations = list(
        itertools.chain.from_iterable(map_intervals(hr, almanac.location_map)
                                      for hr in humiditys)
    )
    return locations


def resolve_part1(input):
    almanac, seeds = parse_almanac(input)
    return min(map_seed_to_location(almanac, seed) for seed in seeds)


def resolve_part2(input):
    almanac, seeds = parse_almanac(input)
    seed_ranges = build_seed_intervals(seeds)
    result_ranges = (map_seed_range(sr, almanac) for sr in seed_ranges)
    return min(r.begin for r in itertools.chain.from_iterable(result_ranges))