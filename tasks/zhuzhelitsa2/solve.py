import random
import requests
from zhuzhelitsa import VerificationError, Zhuzhelitsa, transpose, shuffle, invert, SHUFFLE


API_ENDPOINT = "https://zhuzhelitsa.q.2025.ugractf.ru/api"
API_KEY = "sp5b8hhglb8g5q3l"
ADDRESS = "odtxL3yTxYs924M175iWVV"


def dec(signature: bytes):
    res = requests.post(f"{API_ENDPOINT}/buy_flag", json={
        "api_key": API_KEY,
        "address": ADDRESS,
        "signature": signature.hex(),
    })
    assert res.status_code == 403
    return eval("b" + res.text.split(", got b")[1])


s = set(range(256))
for x in range(0, 256, 4):
    c = dec(b"".join(transpose(bytes([x + i] * 8)) for i in range(4)))
    for i in range(0, 32, 8):
        s &= set(c[i:i + 8])
assert s, "p[0] ^ p[255] = 255"  # Impossible by generation


def guess(p: bytes, c: list[bytes]):
    if len(set(p)) != 256:
        return

    crypto = Zhuzhelitsa(invert(p), True)
    for mask in range(256):
        if c[mask] != crypto._decrypt_block(transpose(bytes([y if (mask >> SHUFFLE[1][j]) & 1 else x for j in range(8)]))):
            return

    print(crypto.p.hex())
    raise SystemExit(0)


while True:
    x = random.randint(0, 255)
    y = random.randint(0, 255)

    c = []
    for mask in range(0, 256, 4):
        c1 = dec(b"".join(transpose(bytes([y if ((mask + i) >> SHUFFLE[1][j]) & 1 else x for j in range(8)])) for i in range(4)))
        c += [c1[i:i + 8] for i in range(0, 32, 8)]

    # p(x) is a subset of p(y) with probability 0.1
    for p_0 in s:
        guess(bytes([
            p_0 ^ sum(1 << i for i in range(8) if c[0][i] != c[mask][i])
            for mask in range(256)
        ]), c)

    # p(x) is a superset of p(y) with probability 0.1
    for p_255 in s:
        guess(bytes([
            p_255 ^ sum(1 << i for i in range(8) if c[255][i] != c[mask][i])
            for mask in range(256)
        ]), c)
