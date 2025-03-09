import math


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


id = "195e3mwru29e51j9c1f13fqqd94em3a0"
passwords = set()
for password_len in range(33, 0, -1):
    rng = to_radix(int(float(int(id + "0" * password_len, 36))), 36)
    if rng[:32] == id:
        passwords.add(rng[32:])

print(*passwords, sep="\n")
