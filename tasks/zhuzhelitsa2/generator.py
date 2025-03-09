from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_secret, get_token
from PIL import Image, ImageChops, ImageFilter
from PIL.Image import Resampling, Transform
import requests
import os


DISABLE_AUTOMATIC_URL = True
GLYPHS: dict[str, Image] = {}
Xw, Yw = 8, 12

with open("/task/private/screenshot.txt") as f:
    Xstart, Ystart = map(int, f.read().split())

with open("/task/private/font.txt") as f:
    font = Image.open("/task/private/font.webp")
    text = f.read().split('\n')
    for y, line in enumerate(text):
        for x, char in enumerate(line):
            GLYPHS[char] = font.crop((x * Xw, y * Yw, (x + 1) * Xw, (y + 1) * Yw))

camera = Image.open("/task/private/PXL_20250227_080754722.JPG")

k = 4096 / 2048
MATRIX = (0.6184833744652438 * k, -0.019520239393421304 * k, -305.6068131813627, 0.05880641901104537 * k, 0.5946619834629123 * k, -990.6446157032346, 0.00006770851146422596 * k, 0.000055944149326219065 * k)


def generate():
    res = requests.post(
        "https://zhuzhelitsa.q.2025.ugractf.ru/api/_init",
        json={
            "api_key": get_token(),
        },
    )
    if res.status_code != 200:
        raise ValueError("Failed to generate")

    addr = get_secret("address2")
    shot = Image.open("/task/private/screenshot.webp")
    for offset_x, char in enumerate(addr):
        shot.paste(GLYPHS[char], (Xstart + offset_x * Xw, Ystart))

    shot = shot.transform(camera.size, Transform.PERSPECTIVE, MATRIX, Resampling.BICUBIC)
    shot = shot.filter(ImageFilter.GaussianBlur(1))
    img = ImageChops.screen(camera, shot)

    os.makedirs(get_attachments_dir(), exist_ok=True)
    img.save(os.path.join(get_attachments_dir(), "IMG_1337.JPG"))

    return {
        "flags": [get_secret("flag2")]
    }
