import os
import random

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag


def generate():
    flag = get_flag()

    random.seed(int(flag.replace("_", ""), 36))

    al = "qwertyuiopasdfghjklzxcvbnm"
    al_tr = list(al)
    while any(i == j for i, j in zip(al, al_tr)):
        random.shuffle(al_tr)
    tr = dict(zip(al, al_tr))

    flag_enc = "".join(tr.get(c, c) for c in flag)

    with open(os.path.join(get_attachments_dir(), "noteasy26.txt"), "w+") as f:
        f.write(flag_enc)
