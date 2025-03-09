from PIL import Image
import os

GLYPHS: dict[str, Image] = {}


def putc(where, offset_x, offset_y, char):
    if char not in GLYPHS:
        GLYPHS[char] = Image.open(f"./private/{char}.png")

    where.paste(GLYPHS[char], (offset_x, offset_y))


def generate():
    flag = "ugra_why_are_you_screaming_at_me_jackdaws_and_big_sphinx_of_quartz_xjblgwfpkdcbzbfcgkzo"

    im = Image.new("RGB", (28 * len(flag), 50), (255, 255, 255))

    for offset_x, char in enumerate(flag):
        putc(im, 28 * offset_x, 0, char)

    im.save("attachments/Untitled.jpg")


generate()
