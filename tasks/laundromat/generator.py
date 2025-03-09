from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_token
import os.path
import struct
import subprocess
import sys
import zlib


TOKEN_PLACEHOLDER = b"GGbfOeqULoSg7CzM"


def generate():
    token = get_token().encode()
    assert len(token) == len(TOKEN_PLACEHOLDER)

    with open("/laundromat", "rb") as f:
        data = f.read()

    assert data.count(TOKEN_PLACEHOLDER) == 1
    data = data.replace(TOKEN_PLACEHOLDER, token)

    # Dear reader: this is not a good solution, but do you have the slightest idea how much time
    # I've wasted on this task already?
    token_placeholder_crc = struct.pack("<L", zlib.crc32(TOKEN_PLACEHOLDER))
    token_crc = struct.pack("<L", zlib.crc32(token))
    assert data.count(token_placeholder_crc) == 2
    data = data.replace(token_placeholder_crc, token_crc)

    binary_path = os.path.join(get_attachments_dir(), "laundromat")
    with open(binary_path, "wb") as f:
        f.write(data)
    os.chmod(binary_path, 0o755)

    subprocess.run(["upx", "-q", "-5", "--lzma", binary_path], stdout=sys.stderr)
