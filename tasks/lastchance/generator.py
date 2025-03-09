#!/usr/bin/env python3

import PIL.Image
import io
import os

if os.environ.get('SOLVER') is None:
    from kyzylborda_lib.generator import get_attachments_dir
    from kyzylborda_lib.secrets import get_flag


# Flag example: "ugra_eepy_thoughts_HELLO1234"
#                ----++++----++++====----====
#                outer/16        inner/12
# Use caps for token-validated part to not mistake start of inner loop (it is zero but...)


def generate_by_bits(flag_as_bits):
    flag_as_bits = flag_as_bits[:]
    for mark in [0x00, 0x1b, 0x2f, 0x43, 0x5e, 0x72, 0x86, 0x99, 0xb8, 0xcb]:
        flag_as_bits.insert(mark, '-')

    carpet = PIL.Image.open(os.path.join("private", "carpet.png"))
    w, h = carpet.size

    colors = {
        '0': (181, 28, 56),
        '1': (117, 129, 127),
        '-': (204, 144, 104),
    }

    im = carpet.load()
    w, h = carpet.size
    for row in range(h):
        for col in range(w):
            r, g, b = im[col, row]
            if r == g == b:
                im[col, row] = colors[flag_as_bits[r]]

    carpet = carpet.resize((2 * w, 2 * h), PIL.Image.NEAREST)
    return carpet


if os.environ.get('SOLVER') is None:
    def generate():
        flag = list(''.join(map(lambda x: bin(ord(x))[2:].rjust(8, '0'), get_flag())))
        pic = generate_by_bits(flag)
        assert_solvable(flag, pic)
        pic.save(os.path.join(get_attachments_dir(), "scanned.png"))


    if __name__ == "__main__":
        generate()


# ================================================================================================ #

def recover(pic):
    # line: x0, y0, dx, dy, count
    lines = [
        # outer top
        (10, 14, 7, 0, 26),

        # outer right
        (190, 18, 0, 7, 19),
        (190, 157, 0, 7, 19),

        # outer bottom
        (-11, -15, -7, 0, 26),

        # outer left
        (5, -19, 0, -7, 19),
        (5, -158, 0, -7, 19),

        # inner top
        (40, 44, 7, 0, 18),

        # inner right
        (160, 49, 0, 7, 30),

        # inner bottom
        (159, -45, -7, 0, 18),

        # inner left
        (35, -50, 0, -7, 30),
    ]

    im = pic.load()

    bits = []
    for x0, y0, dx, dy, count in lines:
        x, y = 2*x0, 2*y0
        for _ in range(count):
            bits.append('0' if im[x, y] == (181, 28, 56) else ('1' if im[x, y] == (117, 129, 127) else '-'))
            x, y = x + 2*dx, y + 2*dy
    return bits


def debug_bitseq(seq):
    r = []
    for i in range(len(seq) // 8):
        r.append(hex(int(''.join(seq[8*i:][:8]), 2))[2:])
    i = 8 * (i + 1)
    return ''.join(r) + ('' if i == len(seq) else ('!' + ''.join(seq[i:])))


def assert_solvable(flag, pic):
    recovered_flag = recover(pic)
    assert flag == recovered_flag, f"Different answers!\nSEND: {debug_bitseq(flag)}\nRECV: {debug_bitseq(recovered_flag)}"


if os.environ.get('__YULIA_SANITY_CHECK') is not None:
    import random

    print("Starting checking Yulia's sanity...")
    for _ in range(16):
        flag = [random.choice('01') for _ in range(28 * 8)]
        pic = generate_by_bits(flag)
        assert_solvable(flag, pic)
    print("She is indeed insane.")

if os.environ.get('SOLVER') is not None:
    s = debug_bitseq(recover(PIL.Image.open(os.environ.get('carpet'))))
    print(''.join(chr(int(s[i:i+2], 16)) for i in range(0, len(s), 2)))
