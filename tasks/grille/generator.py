import os
import pathlib
import sys

try:
    from kyzylborda_lib.generator import get_attachments_dir
    from kyzylborda_lib.secrets import get_flag
    static_dir = pathlib.Path(get_attachments_dir()).parent / "static"
    flag = get_flag()
except ImportError:
    if os.environ.get("FORCE_DEBUG") != "1":
        print(f"Not running under kyzylborda_lib, set FORCE_DEBUG=1", file=sys.stderr)
        raise
    flag = "ugra_score_123r456"
    static_dir = pathlib.Path(".")


def generate():
    assert flag[2] == flag[8] == flag[14]
    assert len(flag) == 18

    source_letters = "1234567890ABCDEF"
    transformed_flag = [
                                      flag[11],
                            flag[0],  flag[10], flag[13],
                  flag[1],  flag[15], flag[2],  flag[9],  flag[12],
        flag[17], flag[16], flag[6],  flag[3],  flag[7],  flag[4], flag[5]
    ]

    with open("triangle-template.svg", "r") as f:
        svg = f.read()

    for s, d in zip(source_letters, transformed_flag):
        svg = svg.replace(f"{s}</tspan>", f"{d}</tspan>")

    static_dir.mkdir(exist_ok=True)
    print(f"Writing to {static_dir}", file=sys.stderr)
    with (static_dir / "triangle.svg").open("w") as f:
        f.write(svg)


if __name__ == "__main__":
    generate()
