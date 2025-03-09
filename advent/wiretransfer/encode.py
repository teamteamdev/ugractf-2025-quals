import random
import sympy

MESSAGE = """ТРАНЗАКЦИЯ

ИСТОЧНИК: ваши карманы
НАЗНАЧЕНИЕ: наши карманы

ЭЛЕКТРОННАЯ ПОДПИСЬ:
ugra_certified_bank_bank_moment_nxflcsobgx7s
Прикрытое акционерное общество «Финансовая Корпорация «Банк Банк Кредитные Системы»
"""

p = 2
while not sympy.isprime(q := random.randint(2 ** 4095, 2 ** 4096 - 1)):
    pass

n = p * q
phi = (p - 1) * (q - 1)

e = 65537
d = pow(e, -1, phi)

m = int.from_bytes(MESSAGE.encode(), "little")
assert m < n
c = pow(m, e, n)

print("n =", n)
print("e =", e)
print("c =", c)
