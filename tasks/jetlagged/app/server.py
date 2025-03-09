#!/usr/bin/env python3

from kyzylborda_lib.secrets import get_flag, validate_token

import aiohttp.web
import aiohttp_jinja2 as jinja2
from jinja2 import FileSystemLoader
import os
import sqlite3
import base64
import io
import qrcode


BASE_DIR = os.path.dirname(__file__)

MAX_ATTEMPTS = 10

ANSWER = (39.858624, -104.668420)

MAX_DISTANCE = 0.0001

STATE_DIR = os.environ.get("STATE_DIR") or "/state"


db = sqlite3.connect(os.path.join(STATE_DIR, "jetlagged.db"), autocommit=True)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS submits(token TEXT, lat DOUBLE, lon DOUBLE)")
cur.execute("CREATE INDEX IF NOT EXISTS submits_token ON submits(token)")

app = aiohttp.web.Application()
routes = aiohttp.web.RouteTableDef()


def get_list(token):
    return cur.execute("SELECT lat, lon FROM submits WHERE token = ?", (token,)).fetchall()


def has_correct_answer(submits):
    return any((abs(lat - ANSWER[0]) < MAX_DISTANCE and abs(lon - ANSWER[1]) < MAX_DISTANCE) for lat, lon in submits)


def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_str


@routes.get("/{token}")
async def slashless(request):
    return aiohttp.web.HTTPMovedPermanently(f"/{request.match_info['token']}/")


@routes.get("/{token}/")
async def main(request):
    if not validate_token(request.match_info["token"]):
        raise aiohttp.web.HTTPForbidden(reason="Invalid token.")

    submits = get_list(request.match_info["token"])
    
    return jinja2.render_template("main.html", request, {
        "token": request.match_info["token"],
        "attempts": max(1 if has_correct_answer(submits) else 0, MAX_ATTEMPTS - len(submits)),
        "max_attempts": MAX_ATTEMPTS,
    })


@routes.get("/{token}/boarding_pass")
async def boarding_pass(request):
    if not validate_token(request.match_info["token"]):
        raise aiohttp.web.HTTPForbidden(reason="Invalid token.")

    submits = get_list(request.match_info["token"])

    if not has_correct_answer(submits):
        raise aiohttp.web.HTTPForbidden(reason="No correct answer.")

    flag = get_flag(request.match_info["token"])
    qr_code = generate_qr_code(flag)
    
    return jinja2.render_template("main.html", request, {
        "token": request.match_info["token"],
        "flag": flag,
        "attempts": max(0, MAX_ATTEMPTS - len(submits)),
        "max_attempts": MAX_ATTEMPTS,
        "qr_code": qr_code,
    })


@routes.post("/{token}/post")
async def post(request):
    token = request.match_info["token"]
    if not validate_token(token):
        raise aiohttp.web.HTTPForbidden(reason="Invalid token.")

    data = await request.post()
    try:
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
    except Exception:
        raise aiohttp.web.HTTPBadRequest(reason="Invalid coordinates.")

    if len(get_list(token)) >= MAX_ATTEMPTS:
        raise aiohttp.web.HTTPNotAcceptable(reason="Too many attempts.")

    cur.execute("INSERT INTO submits(token, lat, lon) VALUES(?, ?, ?)", (token, lat, lon))

    if has_correct_answer(get_list(token)):
        return aiohttp.web.HTTPFound(f"/{token}/boarding_pass")
    else:
        return aiohttp.web.HTTPFound(f"/{token}/")


app.add_routes(routes)
jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))


if __name__ == "__main__":
    if os.environ.get("DEBUG") == "F":
        aiohttp.web.run_app(app, host="0.0.0.0", port=31337)
