import os.path
from weasyprint import HTML

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag


# PART 1. We convert the flag to a C array that should be included in the kernel

def flag_to_c_array(flag: str) -> list[str]:
    flag = flag.encode()

    f = bytearray()
    z = 0x47

    for c in range(0, len(flag), 5):
        f += bytearray([flag[c+3] ^ z, flag[c] ^ z , flag[c+1] ^ z, flag[c+2] ^ z, flag[c+4] ^ z])
        z += 0x17
        z &= 0xff

    return [f"'\\x{i:02x}'," for i in f]

# PART 2. We split string into four parts, returning in order 1 4 3 2

def to_parts(flag_arr: list[str]) -> list[str]:
    total = len(flag_arr)
    assert total % 4 == 0

    part1 = " ".join(flag_arr[:total // 4])
    part2 = " ".join(flag_arr[total // 4:total // 2])
    part3 = " ".join(flag_arr[total // 2:3 * total // 4])
    part4 = " ".join(flag_arr[3 * total // 4:])

    assert f"{part1} {part4}".count(part1) == 1
    assert f"{part1} {part3} {part4}".count(part1) == 1
    return [part1, part4, part3, part2]


# PART 3. We replace in template flag parts
def replace_template(template: str, parts: list[str]) -> str:
    with open(template) as f:
        data = f.read()

    data = data.replace("!!!FLAG1!!!", parts[0])
    data = data.replace("!!!FLAG2!!!", parts[1])
    data = data.replace("!!!FLAG3!!!", parts[2])
    data = data.replace("!!!FLAG4!!!", parts[3])

    return data


def generate():
    flag_arr = flag_to_c_array(get_flag())
    parts = to_parts(flag_arr)
    html = replace_template(os.path.join("dev", "template.html"), parts)
    HTML(string=html).write_pdf(os.path.join(get_attachments_dir(), "patch.pdf"))


def stress():
    import random
    import string
    for _ in range(100000):
        flag = "ugra_please_burn_that_patch_in_the_darkest_pits_of_hell_" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(24))
        flag_arr = flag_to_c_array(flag)
        # Just check asserts work
        to_parts(flag_arr)


if __name__ == "__main__":
    # stress()
    generate()
