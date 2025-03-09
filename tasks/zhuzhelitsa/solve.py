import requests
from zhuzhelitsa import VerificationError, Zhuzhelitsa, transpose, shuffle, invert, SHUFFLE


API_ENDPOINT = "https://zhuzhelitsa.q.2025.ugractf.ru/api"
API_KEY = "sp5b8hhglb8g5q3l"
ADDRESS = "99awU4xtE2NmkxVCbRg-Rq"


def dec(signature: bytes):
    res = requests.post(f"{API_ENDPOINT}/buy_flag", json={
        "api_key": API_KEY,
        "address": ADDRESS,
        "signature": signature.hex(),
    })
    assert res.status_code == 403
    return eval("b" + res.text.split(", got b")[1])


p = []
for x in range(0, 256, 4):
    c = dec(b"".join(shuffle(transpose(bytes([x + i] * 8)), SHUFFLE[1]) for i in range(4)))
    if x == 0:
        p_0_or_255 = c[0]
    for i in range(4):
        p.append(sum((c[8 * i + j] != p_0_or_255) << j for j in range(8)))

# These conditions cannot hold simultaneously because that permutation would be considered unsafe
if p[0] == p_0_or_255:
    pass
elif p[255] ^ 255 == p_0_or_255:
    p = [x ^ 255 for x in p]
else:
    raise ValueError("Failed to recover key")

print(invert(bytes(p)).hex())
