#!/usr/local/bin/python3.9

import collections
import re

FILE_TO_ANALYZE = "rolls-20220403.log"
VERBOSE = False
EXCEPTION_LINES = [
    line.strip() for line in open('exceptions.txt')
]

roll_info_pattern = r'(?P<user>[^:]*):?rolling (?P<num_die>\d+)?d(?P<type_die>\d+)'
roll_info_regex = re.compile(roll_info_pattern)

round_result_pattern = r'^=\d+$'
round_result_regex = re.compile(round_result_pattern)

roll_ends_pattern = r'^\)\+\d+$'
roll_ends_regex = re.compile(roll_ends_pattern)

roll_result_pattern = r'^\d+$'
roll_result_regex = re.compile(roll_result_pattern)


def get_roll_info(line):
    """returns user, num_die, type_die"""
    # TODO: Add a "is_not_a_proper_roll" return value
    result = roll_info_regex.match(line)
    if result is None:
        print("Expected rolling line, but pattern did not match")
        print(f"line: '{line}'\nline num: {i+1}\n")
        raise
    else:
        user = result.group('user')
        num_die = int(result.group('num_die')) if result.group('num_die') else 1
        type_die = int(result.group('type_die'))
        return user, num_die, type_die


def add_roll_stats(type_die, user, rolls, roll_stats):
    if type_die not in roll_stats:
        roll_stats[type_die] = {}
    if user not in roll_stats[type_die]:
        roll_stats[type_die][user] = []
    roll_stats[type_die][user].extend(rolls)

def parse_logs_and_get_roll_stats():
    roll_stats = {}
    last_user = None
    start_collecting_rolls = False
    for i, line in enumerate(open(FILE_TO_ANALYZE)):
        line = line.strip()
        if line.startswith('(From ') or line in EXCEPTION_LINES:
            continue
        elif 'rolling' in line:
            # Step 1
            user, num_die, type_die = get_roll_info(line)
            if not user:
                try:
                    assert last_user is not None
                except:
                    print(f"line: {line}\nline num: {i+1}\n")
                    raise
                user = last_user
            start_collecting_rolls = True
            rolls = []
        elif start_collecting_rolls:
            # Step 2
            # Step 2.a
            if line in ['(', '+']:
                continue
            # Step 2.b - collect rolls:
            elif roll_result_regex.match(line) is not None:
                rolls.append(int(line))
            # Step 2.c
            elif roll_ends_regex.match(line):
                start_collecting_rolls = False
        elif round_result_regex.match(line) is not None:
            # Step 3
            assert start_collecting_rolls == False
            assert len(rolls) == num_die
            add_roll_stats(type_die, user, rolls, roll_stats)
            last_user = user
        else:
            # raise Exception('Unknown Step!\nLine: ' + line)
            if VERBOSE:
                print(f"Unknown Step encountered! Side stepping...\nLine: {line}\nLine Num:{i+1}\n")
    return roll_stats


def print_rolls(rolls, type_die):
    print(f"d{type_die} (total rolls: {len(rolls)})")
    if not rolls:
        return
    rolls_counter = collections.Counter(rolls)
    max_width = len(str(max(rolls_counter.values())))
    
    for roll_num in range(1, type_die+1):
        if roll_num in rolls_counter:
            x_to_print = 'x' * rolls_counter[roll_num]
        else:
            x_to_print = ''
        # print(f'\t{roll_num:2} ({rolls_counter[roll_num]:{max_width}} rolls): {to_print}')
        percentage = f"({rolls_counter[roll_num]/len(rolls):.2%})"
        print(f'\t{roll_num:3} {percentage: >10}: {x_to_print}')

    less_than_half_rolls = sum(1 for roll in rolls if roll <= type_die//2)
    more_than_half_rolls = len(rolls) - less_than_half_rolls
    print(f"1 to {type_die//2} rolls: {less_than_half_rolls / len(rolls):.2%}")
    print(f"{(type_die//2) + 1} to {type_die} rolls: {more_than_half_rolls / len(rolls):.2%}")


def main():
    roll_stats = parse_logs_and_get_roll_stats()
    
    for type_die, obj in roll_stats.items():
        rolls = []
        cidel_rolls = []
        for user, user_rolls in obj.items():
            if user == 'Cidel':
                cidel_rolls.extend(user_rolls)
            else:
                rolls.extend(user_rolls)

        print("\n", "🎲" * 25)

        print("\nFor Cidel")
        print_rolls(cidel_rolls, type_die)
        
        print("\nFor Everyone Else")
        print_rolls(rolls, type_die)

        print("\nEveryone combined")
        print_rolls(rolls + cidel_rolls, type_die)

    print("\n", "🎲" * 25)


main()
