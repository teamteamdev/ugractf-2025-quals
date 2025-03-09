#!/usr/bin/env python3
import difflib
import random
import sys

random.seed(3210)

TABS = ["", "одним символом", "двумя символами", "тремя символами", "четырьмя символами"]

def compute_insertions(file1_lines, file2_lines):
    insertions = []
    global_order = 0
    sm = difflib.SequenceMatcher(None, file1_lines, file2_lines)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'insert':
            for offset in range(j2 - j1):
                base_index = i1
                content = file2_lines[j1 + offset].rstrip('\n')
                if '\\x' in content:
                    content = 'FLAG'
                    insertions.append((base_index, content, global_order))
                    insertions.append((base_index, content, global_order))
                    insertions.append((base_index, content, global_order))
                insertions.append((base_index, content, global_order))
                global_order += 1
        elif tag == 'equal':
            continue
        else:
            raise ValueError(f"Unsupported operation {tag}")
    return insertions

def simulate_random_insertion(insertions):
    random.shuffle(insertions)
    applied = set()
    instructions = []
    for ins in insertions:
        base_index, content, order = ins
        count_before = sum(1 for key in applied if key < (base_index, order))
        effective_index = base_index + count_before
        instructions.append((effective_index, content))
        applied.add((base_index, order))
    return instructions

def main():
    if len(sys.argv) != 3:
        print("Usage: python random_diff.py file1 file2")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        file1_lines = f.readlines()
    with open(sys.argv[2], 'r') as f:
        file2_lines = f.readlines()

    insertions = compute_insertions(file1_lines, file2_lines)
    instructions = simulate_random_insertion(insertions)

    flag_part = 0

    for effective_index, content in instructions:
        if content == 'FLAG':
            flag_part += 1
            if flag_part > 1:
                print(f'<li>строку {effective_index + 1} непосредственно после слов «!!!FLAG1!!!» дополнить строкой следующего содержания: «!!!FLAG{flag_part}!!!»;</li>')
                continue
            content = '!!!FLAG1!!!'
            notabs = content
            tabs = 1
        else:
            notabs = content.lstrip('\t')
            tabs  = len(content) - len(notabs)

        if len(notabs) == 0:
            print(f'<li>после строки {effective_index} дополнить пустой строкой;</li>')
            continue
        print(f'<li>после строки {effective_index} дополнить строкой следующего содержания: «{notabs.replace("<", "&lt;").replace(">", "&gt;")}»', end='')
        if tabs > 0:
            print(f". Строка должна начинаться {TABS[tabs]} табуляции", end='')
        print(';</li>')

if __name__ == '__main__':
    main()
