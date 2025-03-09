from kyzylborda_lib.secrets import get_flag, get_secret, get_token
import requests


DISABLE_AUTOMATIC_URL = True

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"

def to_radix(n: int, radix: int) -> str:
    assert n >= 0
    if n == 0:
        return "0"
    s = ""
    while n != 0:
        s += ALPHABET[n % radix]
        n //= radix
    return s[::-1]


def generate():
    rng = to_radix(int(float(get_secret("rng")) * 1e100), 36)
    password, id = rng[:32], rng[32:]

    res = requests.post(
        f"https://boxcat.q.2025.ugractf.ru/{get_token()}/upload/",
        data={
            "id": id,
            "password": password,
        },
        files={
            "file": ("flag.txt", get_flag() + "\n"),
        },
    )
    if res.status_code not in (200, 409):
        raise ValueError("Failed to generate")

    return {
        "urls": [
            f"https://boxcat.{{hostname}}/{get_token()}/view/{id}/",
        ],
    }
