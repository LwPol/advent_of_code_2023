from typing import NamedTuple, List, Tuple, Dict, Iterable
import itertools
import re


CacheKey = Tuple[str, str]


class SpringsRecord(NamedTuple):
    springs: str
    summary: List[int]


def parse_records(lines: List[str]) -> List[SpringsRecord]:
    def parse_one(line: str) -> SpringsRecord:
        lhs, rhs = line.split()
        return SpringsRecord(springs=lhs, summary=[int(num) for num in rhs.split(',')])
    return list(map(parse_one, lines))


def unfold_records(records: Iterable[SpringsRecord]) -> List[SpringsRecord]:
    def unfold_one(record: SpringsRecord) -> SpringsRecord:
        springs = '?'.join(itertools.repeat(record.springs, 5))
        summary = list(itertools.chain.from_iterable(itertools.repeat(record.summary, 5)))
        return SpringsRecord(springs, summary)
    return list(map(unfold_one, records))


class SubstitutionsAnalysis:
    def __init__(self):
        self.__cache: Dict[CacheKey, int] = {}
    
    def analyse(self, record: SpringsRecord) -> int:
        return self.impl_cached(record.springs + '.', 0, record.summary)

    def eval_cache_key(self, pattern: str, summary: List[int]) -> CacheKey:
        return pattern, ' '.join(map(str, summary))

    def impl_cached(self, pattern: str, current_group_size: int, summary: List[int]) -> int:
        if current_group_size == 0:
            key = self.eval_cache_key(pattern, summary)
            if key in self.__cache:
                return self.__cache[key]
        
        result = self.impl(pattern, current_group_size, summary)
        if current_group_size == 0:
            self.__cache[self.eval_cache_key(pattern, summary)] = result
        return result

    def impl(self, pattern: str, current_group_size: int, summary: List[int]) -> int:
        if pattern == '':
            return 1 if not summary else 0
        
        spring = pattern[0]
        if spring == '#':
            if current_group_size > 0:
                new_size = current_group_size + 1
                if new_size > summary[0]:
                    return 0
                return self.impl(pattern[1:], new_size, summary)
            if summary:
                return self.impl(pattern[1:], 1, summary)
            return 0
        if spring == '.':
            if current_group_size > 0:
                if current_group_size == summary[0]:
                    return self.impl_cached(pattern[1:], 0, summary[1:])
                return 0
            return self.impl_cached(pattern[1:], 0, summary)
        if spring == '?':
            return (self.impl_cached('#' + pattern[1:], current_group_size, summary) + 
                    self.impl_cached('.' + pattern[1:], current_group_size, summary))


def resolve_part1(input):
    records = parse_records(input)
    analysis = SubstitutionsAnalysis()
    return sum(analysis.analyse(record) for record in records)


def resolve_part2(input):
    records = unfold_records(parse_records(input))
    analysis = SubstitutionsAnalysis()
    return sum(analysis.analyse(record) for record in records)