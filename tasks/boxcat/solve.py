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


id = "sptw6wta0l82g626h2c2c35r80xytdxj4"

m1 = 36 ** len(id)
x = int(id, 36)

min_n = 36 ** (32 + len(id) - 1)
m2 = int(math.nextafter(min_n, float("+inf")) - min_n)

# n = x (mod m1), n = 0 (mod m2)

g = math.gcd(m1, m2)
assert x % g == 0
x //= g
m1 //= g
m2 //= g

n = (x * pow(m2, -1, m1)) % m1 * m2 * g
s = to_radix(n, 36)

assert s[32:] == id
print(s[:32])
