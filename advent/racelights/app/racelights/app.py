import asyncio
import datetime
import fcntl
import json
import math
import os
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

def haversine_to_target(lat1, lon1):
    lat2 = 57.679125
    lon2 = 11.932030

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    r = 6371000
    return c * r

project = Path(__file__).parent
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    middleware=[
        Middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"]),
    ]
)
STATE_PATH = os.environ.get("STATE_PATH", str(project))
app.mount("/static", StaticFiles(directory=project / "static"), name="static")
templates = Jinja2Templates(directory=project / "templates")

# Create a global variable to hold the client
client: httpx.AsyncClient = None

@app.on_event("startup")
async def startup_event():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()


@app.get("/")
async def index(request: Request) -> HTMLResponse:
    request.session.setdefault("session", str(uuid.uuid4()))
    return templates.TemplateResponse(request, "index.html", {})


class Coords(BaseModel):
    lat: float
    lon: float


class Report(BaseModel):
    coords: Coords
    captcha: str

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_KEY", "")


@app.post("/report")
async def post(request: Request, report: Report) -> JSONResponse:
    global RECAPTCHA_SECRET_KEY

    request.session.setdefault("session", str(uuid.uuid4()))

    if RECAPTCHA_SECRET_KEY == "":
        try:
            with open(f"{STATE_PATH}/key") as key:
                RECAPTCHA_SECRET_KEY = key.read().strip()
        except FileNotFoundError:
            return JSONResponse(status_code=500, content={"message": "Recaptcha secret key not set"})

    response = await client.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": RECAPTCHA_SECRET_KEY,
            "response": report.captcha,
        }
    )
    result = response.json()

    if not result.get("success"):
        return JSONResponse(status_code=400, content={"message": "Recaptcha failed"})

    is_correct = haversine_to_target(report.coords.lat, report.coords.lon) <= 50

    await asyncio.to_thread(
        append_log,
        json.dumps({
            "timestamp": datetime.datetime.now().isoformat(),
            "browser_id": request.session["session"],
            "coords": {"lat": report.coords.lat, "lon": report.coords.lon},
            "is_correct": is_correct
        })
    )

    if is_correct:
        return JSONResponse(status_code=200, content={"message": "Your report is registered under Number ugra_ingen_ko_pa_isen_xunhq9m3ctts\n\nThanks for cooperating!"})

    return JSONResponse(status_code=200, content={"message": "ERROR: Satellite check detected surface mismatch. Check your coordinates!"})


def append_log(record: str):
    # Please run asyncio.to_thread(append_log, record)
    with open(f"{STATE_PATH}/attempt_log.jsonl", "a") as log:
        fcntl.flock(log, fcntl.LOCK_EX)
        print(record, file=log)
        fcntl.flock(log, fcntl.LOCK_UN)
