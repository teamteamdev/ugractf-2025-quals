from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
import sys

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag


background = Image.open("private/unsplash.png").convert("RGBA")
font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationMono-Regular.ttf", 22)


def small_numbers():
    sum = 0
    while True:
        for dr in range(sum + 1):
            for dg in range(sum + 1 - dr):
                for db in range(sum + 1 - dr - dg):
                    yield dr, dg, db, sum - dr - dg - db
        sum += 1


def generate():
    flag = get_flag()
    left, top, right, bottom = font.getbbox(flag)

    for dr, dg, db, da in small_numbers():
        text = Image.new("RGBA", (right - left, bottom - top))
        draw = ImageDraw.Draw(text)
        draw.text((-left, -top), flag, font=font, fill=(255 - dr, 255 - dg, 255 - db, 255 - da))
        text = text.rotate(-30, Image.Resampling.BICUBIC, expand=True)
        text = text.crop((0, 0, *background.size))

        io = BytesIO()
        Image.alpha_composite(background, text).save(io, "png")
        png = io.getvalue()

        # This underestimates problem difficulty with very low probability -- significantly lower
        # than 0.02%, the exact probability is hard to compute.
        if png.count(b"\r\n") >= 5 and all(chunk.count(b"\r\n") <= 2 for chunk in png.split(b"IDAT")):
            break

        print("Regenerating...", file=sys.stderr)

    with open(os.path.join(get_attachments_dir(), "flag.png"), "wb") as f:
        f.write(png.replace(b"\r\n", b"\n"))
