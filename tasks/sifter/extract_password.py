def rbt(n):
    return sum(((n >> (7 - i)) & 1) << i for i in range(8))

def ror(n, k):
    return ((n * 257) >> k) & 255


# Оригинальный код по prog.asm
# for _ in range(4):
#     F = ror(F, 3) - H
#     D = D ^ F ^ 255
#     B = ror(B, 2) + G - 1
#     A = rbt(A) ^ D
#     C = ror(C, 1) ^ A
#     D = D + 1 + B
#     E = rbt(E) ^ B
#     G = ~G + F - 1 == (F - G) - 2
#     H = H ^ C


[A, B, C, D, E, F, G, H] = [0x2c, 0x26, 0x50, 0x9c, 0xd5, 0xc5, 0xda, 0xb1]

for _ in range(4):
    H ^= C
    G = ((G + 1 - F) % 256) ^ 255
    E = rbt(E ^ B)
    D = (D - 1 - B) % 256
    C = ror(C ^ A, 7)
    A = rbt(A ^ D)
    B = ror((B - G + 1) % 256, 6)
    D = D ^ F ^ 255
    F = ror((F + H) % 256, 5)

password = [A, B, C, D, E, F, G, H]

print(bytes(password)[::-1].decode())
