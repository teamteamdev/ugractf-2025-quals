import itertools
import struct
import zlib


data = open("flag.png", "rb").read()


iend_i = data.rfind(b"IEND")
idat_i = data.find(b"IDAT")

recovered_idat = []

while idat_i < iend_i:
    next_i = data.find(b"IDAT", idat_i + 4)
    if next_i == -1:
        next_i = iend_i
    chunk = data[idat_i - 4:next_i - 4]
    idat_i = next_i

    stored_length = len(chunk) - 12
    expected_length, = struct.unpack(">L", chunk[:4])

    stored_body = chunk[8:-4]
    expected_crc, = struct.unpack(">L", chunk[-4:])

    lf_positions = [i for i, c in enumerate(stored_body) if c == b"\n"[0]]

    for insert_cr_at in itertools.combinations(lf_positions, expected_length - stored_length):
        fixed_body = stored_body
        for i in insert_cr_at[::-1]:
            fixed_body = fixed_body[:i] + b"\r" + fixed_body[i:]

        if zlib.crc32(b"IDAT" + fixed_body) == expected_crc:
            print("Chunk recovered")
            recovered_idat.append(fixed_body)
            break
    else:
        assert False, "Failed to recover chunk"


ihdr_i = data.find(b"IHDR")
ihdr_length, = struct.unpack(">L", data[ihdr_i - 4:ihdr_i])
ihdr = data[ihdr_i - 4:ihdr_i + 8 + ihdr_length]


def write_chunk(type: bytes, content: bytes):
    f.write(struct.pack(">L", len(content)) + type + content + struct.pack(">L", zlib.crc32(type + content)))


with open("recovered.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")
    f.write(ihdr)
    for idat in recovered_idat:
        write_chunk(b"IDAT", idat)
    write_chunk(b"IEND", b"")
