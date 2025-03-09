#!/usr/bin/env python3

from kyzylborda_lib.secrets import get_flag, validate_token

import aiohttp.web
import aiohttp_jinja2 as jinja2
from jinja2 import FileSystemLoader
import os
import sys
import sqlite3


BASE_DIR = os.path.dirname(__file__)

MAX_ATTEMPTS = 7

ANSWER = (-26.8170836, -65.1986317)

MAX_DISTANCE = 0.01

STATE_DIR = os.environ.get("STATE_DIR") or "/state"


db = sqlite3.connect(os.path.join(STATE_DIR, "beardbox.db"), autocommit=True)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS submits(token TEXT, lat DOUBLE, lon DOUBLE)")
cur.execute("CREATE INDEX IF NOT EXISTS submits_token ON submits(token)")

app = aiohttp.web.Application()
routes = aiohttp.web.RouteTableDef()
# routes.static("/static", os.path.join(BASE_DIR, "static"))


def get_list(token):
    return cur.execute("SELECT lat, lon FROM submits WHERE token = ?", (token,)).fetchall()


def has_correct_answer(submits):
    return any((abs(lat - ANSWER[0]) < MAX_DISTANCE and abs(lon - ANSWER[1]) < MAX_DISTANCE) for lat, lon in submits)


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
        "attempts": max(0, MAX_ATTEMPTS - len(submits)),
        "max_attempts": MAX_ATTEMPTS,
        "flag": get_flag(request.match_info["token"]) if has_correct_answer(submits) else None,
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

    return aiohttp.web.HTTPFound(f"/{token}/")


app.add_routes(routes)
jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))


if __name__ == "__main__":
    if os.environ.get("DEBUG") == "F":
        aiohttp.web.run_app(app, host="0.0.0.0", port=31337)
