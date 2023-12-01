import re


def extract_calibration(line: str) -> int:
    digits = list(filter(lambda c: c.isdigit(), line))
    return int(f'{digits[0]}{digits[-1]}')


def enumerate_calibration_digits(line: str) -> int:
    substitutions = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'seven': 7, 'eight': 8, 'nine': 9
    }
    regex = re.compile('|'.join(substitutions.keys()) + '|\d')
    start_idx = 0
    while (match := regex.search(line, start_idx)) is not None:
        if match.group(0) in substitutions.keys():
            yield str(substitutions[match.group(0)])
        else:
            yield match.group(0)
        start_idx = match.start() + 1


def extract_calibration_aligned(line: str) -> int:
    digits = list(enumerate_calibration_digits(line))
    return int(f'{digits[0]}{digits[-1]}')


def resolve_part1(input):
    return sum(extract_calibration(l) for l in input)


def resolve_part2(input):
    return sum(extract_calibration_aligned(l) for l in input)