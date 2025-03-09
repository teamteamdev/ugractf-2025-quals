from flask import Flask, request, send_file
from kyzylborda_lib.secrets import get_secret, validate_token
import secrets
import sqlite3
from zhuzhelitsa import VerificationError, Zhuzhelitsa


app = Flask(__name__)


con = sqlite3.connect("/state/accounts.db", autocommit=True)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS accounts(api_key TEXT, address TEXT, private_key BLOB, hardened BOOL, balance INTEGER)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS accounts_api_key_address ON accounts(api_key, address)")


@app.route("/")
def index():
    return send_file("static/index.html")


@app.route("/api/_init", methods=["POST"])
def init():
    req = request.json
    if not isinstance(req, dict) or not isinstance(req.get("api_key"), str):
        return "Malformed request", 400
    api_key = req["api_key"]

    if not validate_token(api_key):
        return "Invalid API key", 401

    address1 = get_secret("address1", api_key)
    private_key1 = Zhuzhelitsa(get_secret("rng_seed1", api_key), False).p

    address2 = get_secret("address2", api_key)
    private_key2 = Zhuzhelitsa(get_secret("rng_seed2", api_key), True).p

    for row in [
        (api_key, address1, private_key1, False, 100),
        (api_key, address2, private_key2, True, 200),
    ]:
        try:
            cur.execute(
                "INSERT INTO accounts(api_key, address, private_key, hardened, balance) VALUES (?, ?, ?, ?, ?)",
                row,
            )
        except sqlite3.IntegrityError:
            # Already initialized
            pass

    return "OK"


@app.route("/api/register", methods=["POST"])
def register():
    req = request.json
    if not isinstance(req, dict) or not isinstance(req.get("api_key"), str) or not isinstance(req.get("hardened"), bool):
        return "Malformed request", 400
    api_key = req["api_key"]
    hardened = req["hardened"]

    if not validate_token(api_key):
        return "Invalid API key", 401

    address = secrets.token_urlsafe(16)
    private_key = Zhuzhelitsa(None, hardened).p

    cur.execute(
        "INSERT INTO accounts(api_key, address, private_key, hardened, balance) VALUES (?, ?, ?, ?, ?)",
        (api_key, address, private_key, hardened, 0),
    )

    return {
        "address": address,
        "private_key": private_key.hex(),
    }


@app.route("/api/status", methods=["POST"])
def status():
    req = request.json
    if not isinstance(req, dict) or not isinstance(req.get("api_key"), str) or not isinstance(req.get("address"), str):
        return "Malformed request", 400
    api_key = req["api_key"]
    address = req["address"]

    if not validate_token(api_key):
        return "Invalid API key", 401

    row = cur.execute(
        "SELECT hardened, balance FROM accounts WHERE api_key = ? AND address = ?",
        (api_key, address),
    ).fetchone()
    if row is None:
        return "Address not registered", 404
    hardened, balance = row

    return {
        "hardened": hardened,
        "balance": balance,
    }


@app.route("/api/buy_flag", methods=["POST"])
def buy_flag():
    req = request.json
    if not isinstance(req, dict) or not isinstance(req.get("api_key"), str) or not isinstance(req.get("address"), str) or not isinstance(req.get("signature"), str):
        return "Malformed request", 400

    api_key = req["api_key"]
    address = req["address"]
    try:
        signature = bytes.fromhex(req["signature"])
    except ValueError:
        return "Malformed request", 400

    if not validate_token(api_key):
        return "Invalid API key", 401

    row = cur.execute(
        "SELECT private_key, hardened, balance FROM accounts WHERE api_key = ? AND address = ?",
        (api_key, address),
    ).fetchone()
    if row is None:
        return "Address not registered", 404
    private_key, hardened, balance = row

    subject = f"ОФОРМИТЬ АКТ купли-продажи НАД флагом НА СРЕДСТВА СО СЧЁТА {address}".encode()
    crypto = Zhuzhelitsa(private_key, hardened)
    try:
        crypto.verify(subject, signature)
    except VerificationError as e:
        return e.message, 403

    if balance < (200 if hardened else 100):
        return "Insufficient funds", 402

    return {
        "flag": get_secret("flag2" if hardened else "flag1", api_key),
    }
