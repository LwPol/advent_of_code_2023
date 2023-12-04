from typing import NamedTuple, Iterable, Set, Dict, Tuple
import re


class Card(NamedTuple):
    winning: Set[int]
    numbers: Set[int]


def parse_cards(lines: Iterable[str]) -> Dict[int, Card]:
    def parse_one(line: str) -> Tuple[int, Card]:
        colon_idx = line.find(':')
        card_id = int(line[5:colon_idx])
        nums_str = line[colon_idx + 1:].split('|')
        return card_id, Card(
            winning={int(n) for n in re.findall(r'\d+', nums_str[0])},
            numbers={int(n) for n in re.findall(r'\d+', nums_str[1])})
    return dict(map(parse_one, lines))


def score_card(card: Card) -> int:
    winning = len(card.winning & card.numbers)
    return 2 ** (winning - 1) if winning > 0 else 0


def score_cards(cards: Iterable[Card]) -> int:
    return sum(map(score_card, cards))


def count_scratchcards(cards: Dict[int, Card]) -> int:
    copies = {card_id: 1 for card_id in cards.keys()}
    current_card_id = 1
    while current_card_id < len(cards):
        new_cards = len(cards[current_card_id].winning & cards[current_card_id].numbers)
        for i in range(new_cards):
            copies[current_card_id + i + 1] += copies[current_card_id]
        current_card_id += 1
    return sum(copies.values())


def resolve_part1(input):
    return score_cards(parse_cards(input).values())


def resolve_part2(input):
    return count_scratchcards(parse_cards(input))