import os
import shutil
import subprocess
import tempfile

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag


def generate():
    with open("/main.exe", "rb") as src:
        with open(os.path.join(get_attachments_dir(), "flag.exe"), "w+b") as dst:
            dst.write(src.read().replace(
                "ugra_flag_stub_ccccccccccccccccccccccccccccccccccccccccccc".encode('utf-16le'),
                get_flag().encode('utf-16le')
            ))
