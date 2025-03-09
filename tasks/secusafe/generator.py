from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag

import base64
import os.path


a1 = b'\x93\xab\x9e\x03\x16\xbe<Eg\x94\x8e^\t\x17\xff\x9bK[\xe513y\x99\xa3\x7f\x0cN\x18\xc3\xdcDR]\xb5s\xa9\x10\xd6Z\x8f\xe0|\xe9\n\xcd\x0b\x8c\xd4\x005*\x0f\xa2\\?tv\'\xa8}\xc9\xc7%\x90!\xb6\xea\x1b\xd7\xb4\xd2\x9f\xfb\xa7\xf2&@\xebjC\xbf\xd8\x1d\xd0\xb9\xe3\r\xb7\xc6,\x1e$\xa0\x9ax\x83OJ\xb1\xb8\xa4\x8ard\xc1\x86\x132/B\x81=\xb3\xee\xcaX4h\xba\xb0M\x9c\xb2\x12\xda\xc5`a\xf9\x84\xbb\x9d\x15;n\xfcl\x98\x89+\xfa\xa5A\xf6\xa6-\xf5bz\x19\x91\x02\x96\xaa>\xc2\xdf7 m\x01W\x82\xf0\x97\xec\x07.U\xc4\xad#\x95\xf3i\xfe9\x85\x04P\xe2\x11\xe6\xafS\xdd\xbcp\xe4\xd9\x08\x80\x14\x1f\x0eo\xae\xf4T"\x1c\xe18\xed\x87\xfdqY~\x056e\x88\x8b\xf7F\xf1k\xef\xcc(\xbd\x1a\xc0Lc\xcb\x8dw\xd5G0\xe8\xdb\xa1Q\xd3H\xf8VIu\xde\xce_:\xd1\x06{\xc8\xac\xcf\x92)\xe7f'
a2 = b'0\xa0\x97\x03\xb2\xd1\xf7\xa6\xbe\x0c+-\x19V\xc23$\xb5{j\xc0\x84\x04\r\x1b\x95\xdeC\xc8RZ\xc1\x9e@\xc7\xab[>K9\xdc\xfd2\x8bY\x91\xa7l\xe7\x13k\x14t1\xd2\x9d\xca\xb0\xf5\x85\x06o\x9a6L\x8emO\x1e\x07\xd7\xe6\xed\xf0a\x10\xe0x\x1a`\xb3\xeb\x1f\xb8\xc6\xa8\xef\xa1s\xcf&\x115 \x0b\xf4~\x7f\x93\xe1g\xd3\xff\x08u\xaeN\xd9\x88\x9f\x86\xc3\xbb\xcef"7\xf18\xe4^\x15\x94\xf8);\xd0\x18\xbfn\xa2_\x81\xb1i\xcc\xd4\x8ae\xd5.\xe3\n\'?\x96\xfc\x00\t\xac\x98\xa4\x89\x16]\x0fy\x83\x02G\\\xea4\x17d\x8d\x90I:#\x99\x01\xfa\xaa\xc4\xb7wbzpE!AWcTv\x82\xba\xdd\x05P\xdfh\x9b\x1c\xa9}X=\xf9<r\xe2\xdb,\xf3\xfbS\xf6F\xec/\xe5%DQ\xbd|\xe9\x1d\xb9\xf2\x9c(\xc9\xb4U\xbc\x12\xb6\xfe\xe8*BM\xa5\xcbq\xda\xa3\xd8J\xad\xc5\x92\x8f\xd6\xee\x80\x8cH\x87\xcd\xaf\x0e'

unk1 = bytes([0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54])


def key_schedule(key: bytes) -> bytes:
    assert len(key) == 16

    schedule = bytearray([0] * 176)
    schedule[:16] = key

    i = 16
    i2 = 1
    while i < 176:
        tmp = schedule[i - 4:i]

        if i % 16 == 0:
            tmp[0], tmp[1], tmp[2], tmp[3] = tmp[1], tmp[2], tmp[3], tmp[0]
            for j in range(4):
                tmp[j] = a1[tmp[j]]
            tmp[0] ^= unk1[i2]
            i2 += 1

        for j in range(4):
            schedule[191 - i] = schedule[i - 16] ^ tmp[j]
            i += 1

    return bytes(schedule)


def xor(input: bytearray, schedule: bytes, i: int):
    for j in range(16):
        input[j] ^= schedule[i * 16 + j]


def sub_bytes(input: bytearray, inv: bool):
    for i in range(16):
        if inv:
            input[i] = a2[input[i]]
        else:
            input[i] = a1[input[i]]


def shift(input: bytearray, inv: bool):
    if inv:
        input[5], input[9], input[13], input[1] = input[1], input[5], input[9], input[13]
        input[2], input[10] = input[10], input[2]
        input[6], input[14] = input[14], input[6]
        input[11], input[7], input[3], input[15] = input[15], input[11], input[7], input[3]
    else:
        input[1], input[5], input[9], input[13] = input[5], input[9], input[13], input[1]
        input[10], input[2] = input[2], input[10]
        input[14], input[6] = input[6], input[14]
        input[15], input[11], input[7], input[3] = input[11], input[7], input[3], input[15]


def magic(a, b):
    res = 0
    while b != 0:
        if (b & 1) != 0:
            res ^= a
        a <<= 1
        if (a & 256) != 0:
            a ^= 283
        b >>= 1
    return res


def mul(input: bytearray, inv: bool):
    for i in range(4):
        a, b, c, d = input[i * 4:i * 4 + 4]
        if inv:
            input[i * 4:i * 4 + 4] = (
                magic(14, a) ^ magic(11, b) ^ magic(13, c) ^ magic(9, d),
                magic(9, a) ^ magic(14, b) ^ magic(11, c) ^ magic(13, d),
                magic(13, a) ^ magic(9, b) ^ magic(14, c) ^ magic(11, d),
                magic(11, a) ^ magic(13, b) ^ magic(9, c) ^ magic(14, d),
            )
        else:
            input[i * 4:i * 4 + 4] = (
                magic(2, a) ^ magic(3, b) ^ magic(1, c) ^ magic(1, d),
                magic(1, a) ^ magic(2, b) ^ magic(3, c) ^ magic(1, d),
                magic(1, a) ^ magic(1, b) ^ magic(2, c) ^ magic(3, d),
                magic(3, a) ^ magic(1, b) ^ magic(1, c) ^ magic(2, d),
            )


def aes(data: bytes, key: bytes, inv: bool) -> bytes:
    schedule = key_schedule(key)
    output = bytearray()

    if not inv:
        pad = 16 - len(data) % 16
        data += bytes([pad]) * pad

    for i in range(0, len(data), 16):
        block = bytearray(data[i:i + 16])

        if inv:
            xor(block, schedule, 10)
            for j in range(9, 0, -1):
                shift(block, True)
                sub_bytes(block, True)
                xor(block, schedule, j)
                mul(block, True)
            sub_bytes(block, True)
            shift(block, True)
            xor(block, schedule, 0)
        else:
            xor(block, schedule, 0)
            for j in range(1, 10):
                sub_bytes(block, False)
                shift(block, False)
                mul(block, False)
                xor(block, schedule, j)
            sub_bytes(block, False)
            shift(block, False)
            xor(block, schedule, 10)

        output += block

    if inv:
        output = output[:-output[-1]]

    return bytes(output)


def generate():
    with open(os.path.join(get_attachments_dir(), "flag.enc"), "w") as f:
        f.write(base64.b64encode(aes(get_flag().encode(), b"1234567890\x00\x00\x00\x00\x00\x00", False)).decode() + "\n")
