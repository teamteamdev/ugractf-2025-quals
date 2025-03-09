#!/usr/bin/env python3

import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import os
import random
import tempfile
import math
import subprocess
import tqdm
import colorsys

random.seed(8848)

if __name__ == "__main__":
    W = 320
    H = 240

    font = PIL.ImageFont.truetype(os.path.expanduser("~/.fonts/Inter Desktop/Inter-Black.otf"), 100)

    for letter in tqdm.tqdm("abcdefghijklmnopqrstuvwxyz0123456789_#"):
        hue = random.random()
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = tuple(int(255 * x) for x in rgb)
        cx = random.randint(int(W * 0.4), int(W * 0.6))
        cy = random.randint(int(H * 0.4), int(H * 0.6))
        angle = random.uniform(0, 360)
        direction_x, direction_y = math.sin(math.radians(angle)), math.cos(math.radians(angle))
        bbox = font.getbbox(letter)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        with tempfile.TemporaryDirectory() as tmpdir:
            for frame in range(-40, 20):
                img = PIL.Image.new("RGB", (W, H), "black")
                draw = PIL.ImageDraw.Draw(img)
                for trace in range(20):
                    offset = ((frame + trace) / 20) ** 3
                    lx = cx + direction_x * offset * W
                    ly = cy + direction_y * offset * H
                    lc = tuple(int(c * ((trace / 20) ** 2)) for c in color)
                    draw.text((int(lx - text_w / 2), int(ly - text_h / 2)), letter, font=font, fill=lc)
                img.save(os.path.join(tmpdir, f"{frame + 40:04d}.png"))
            video_file = os.path.join(tmpdir, "letter.ts")
            subprocess.check_call(["ffmpeg", "-y", "-framerate", "25", "-f", "image2",
                                   "-i", os.path.join(tmpdir, "%04d.png"),
                                   "-c:v", "libx264", "-q:v", "28",
                                   "-f", "mpegts", video_file])
            os.rename(video_file, f"{letter}.ts")