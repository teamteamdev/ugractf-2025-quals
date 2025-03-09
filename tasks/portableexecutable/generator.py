import os

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag


def generate():
    with open("/task/src/main.exe", "rb") as src:
        with open(os.path.join(get_attachments_dir(), "flag.exe"), "w+b") as dst:
            f = b''.join(eval("b'\\" + hex(ord(c)^0x80)[1:] + "'") for c in get_flag())
            dst.write(src.read().replace(b'\xCC'*48, f))
