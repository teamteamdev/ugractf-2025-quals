import hashlib
import random
from typing import Optional


__all__ = ("VerificationError", "Zhuzhelitsa")


SHUFFLE = [
    bytes([7, 4, 1, 5, 3, 2, 0, 6]),
    bytes([0, 4, 2, 3, 7, 6, 5, 1]),
    bytes([1, 5, 0, 2, 4, 3, 7, 6]),
]

INV_SHUFFLE = [
    bytes([6, 2, 5, 4, 1, 3, 7, 0]),
    bytes([0, 7, 2, 3, 1, 6, 5, 4]),
    bytes([2, 0, 3, 5, 4, 1, 7, 6]),
]


def generate_random_cyclic_permutation(rng: random.Random) -> bytes:
    cycle = []
    used = [False] * 256
    for _ in range(256):
        while used[(byte := rng.randint(0, 255))]:
            pass
        cycle.append(byte)
        used[byte] = True

    p = bytearray([0] * 256)
    for i in range(256):
        p[cycle[i - 1]] = cycle[i]
    return bytes(p)


def is_safe_permutation(p: bytes) -> bool:
    return all(p[i ^ 0xff] != p[i] ^ 0xff for i in range(128))


def permute(block: bytes, p: bytes) -> bytes:
    return bytes([p[byte] for byte in block])


def transpose(block: bytes) -> bytes:
    return bytes([
        sum(((block[i] >> j) & 1) << i for i in range(8))
        for j in range(8)
    ])


def shuffle(block: bytes, shuffle: bytes) -> bytes:
    return bytes([block[shuffle[i]] for i in range(8)])


def invert(p: bytes) -> bytes:
    p_inv = bytearray([0] * 256)
    for i, x in enumerate(p):
        p_inv[x] = i
    return bytes(p_inv)


class Zhuzhelitsa:
    def __init__(self, p: Optional[str | bytes], hardened: bool):
        if not isinstance(p, bytes):
            rng = random.Random(p)
            while not is_safe_permutation(p := generate_random_cyclic_permutation(rng)):
                pass
        self.p = p

        self.p_inv = invert(p)

        self.rounds = 3 if hardened else 2


    def _encrypt_block(self, block: bytes) -> bytes:
        for i in range(self.rounds):
            block = shuffle(transpose(permute(block, self.p)), SHUFFLE[i])
        return block


    def _decrypt_block(self, block: bytes) -> bytes:
        for i in range(self.rounds - 1, -1, -1):
            block = permute(transpose(shuffle(block, INV_SHUFFLE[i])), self.p_inv)
        return block


    def sign(self, data: bytes) -> bytes:
        hashed = hashlib.sha256(data).digest()
        return b"".join(self._encrypt_block(hashed[i:i + 8]) for i in range(0, 32, 8))


    def verify(self, data: bytes, signature: bytes):
        if len(signature) != 32:
            raise VerificationError(f"Wrong signature length: expected 32, got {len(signature)}")

        hashed_expected = hashlib.sha256(data).digest()
        hashed_actual = b"".join(self._decrypt_block(signature[i:i + 8]) for i in range(0, 32, 8))
        if hashed_expected != hashed_actual:
            raise VerificationError(f"Wrong decoded hash: expected {hashed_expected!r}, got {hashed_actual!r}")


class VerificationError(Exception):
    def __init__(self, message: str):
        self.message = message
