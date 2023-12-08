from typing import Iterable, List, Tuple, Dict, Type
from collections import Counter
from enum import IntEnum


CARDS_MAPPING = {
    c: val for c, val
    in zip(['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'], range(1, 100))
}

CARDS_MAPPING_WITH_JOKER = {
    c: val for c, val
    in zip(['J', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'Q', 'K', 'A'], range(1, 100))
}


class HandKind(IntEnum):
    HIGH_CARDS = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE = 3
    FULL = 4
    FOUR = 5
    FIVE = 6


def parse_hands(lines: Iterable[str]) -> List[Tuple[str, int]]:
    def parse_one(line: str) -> Tuple[str, int]:
        card, bid = line.split()
        return card, int(bid)
    return list(map(parse_one, lines))


def determine_kind(dist: Counter) -> HandKind:
    values = sorted(dist.values(), reverse=True)
    if values == [5]:
        return HandKind.FIVE
    if values == [4, 1]:
        return HandKind.FOUR
    if values == [3, 2]:
        return HandKind.FULL
    if values == [3, 1, 1]:
        return HandKind.THREE
    if values == [2, 2, 1]:
        return HandKind.TWO_PAIR
    if values == [2, 1, 1, 1]:
        return HandKind.PAIR
    return HandKind.HIGH_CARDS


def hand_to_kind(cards: str) -> HandKind:
    return determine_kind(Counter(cards))


def hand_to_kind_with_joker(cards: str) -> HandKind:
    items = Counter(cards)
    jokers = items.get('J', 0)
    del items['J']
    if jokers == 5 or jokers == 4:
        return HandKind.FIVE
    s = items.most_common()[0][0]
    items[s] += jokers
    return determine_kind(items)


def compare_cards(lhs: str, rhs: str, mapping: Dict[str, int]) -> bool:
    for l, r in zip(lhs, rhs):
        if l != r:
            return mapping[l] < mapping[r]
    return False


class HandComparator:
    def __init__(self, cards: str):
        self.cards = cards

    def __lt__(self, other: "HandComparator") -> bool:
        kind1, kind2 = hand_to_kind(self.cards), hand_to_kind(other.cards)
        if kind1 != kind2:
            return kind1 < kind2
        return compare_cards(self.cards, other.cards, CARDS_MAPPING)


class HandJokerComparator:
    def __init__(self, cards: str):
        self.cards = cards
    
    def __lt__(self, other: "HandComparator") -> bool:
        kind1, kind2 = hand_to_kind_with_joker(self.cards), hand_to_kind_with_joker(other.cards)
        if kind1 != kind2:
            return kind1 < kind2
        return compare_cards(self.cards, other.cards, CARDS_MAPPING_WITH_JOKER)


def get_total_winnings(hands: List[Tuple[str, int]], comparatorType: Type) -> int:
    hands.sort(key=lambda x: comparatorType(x[0]))
    return sum(rank * item[1] for rank, item in enumerate(hands, start=1))


def resolve_part1(input):
    return get_total_winnings(parse_hands(input), HandComparator)


def resolve_part2(input):
    return get_total_winnings(parse_hands(input), HandJokerComparator)