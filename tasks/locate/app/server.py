from flask import Flask, render_template, request
from kyzylborda_lib.secrets import get_flag, validate_token
import sqlite3


MAX_ATTEMPTS = 7
ANSWER = (-4144, -4895)


con = sqlite3.connect("/state/submits.db", autocommit=True)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS submits(token TEXT, x INTEGER, z INTEGER)")
cur.execute("CREATE INDEX IF NOT EXISTS submits_token ON submits(token)")


def get_list(token: str) -> list[tuple[int, int]]:
    return cur.execute("SELECT x, z FROM submits WHERE token = ?", (token,)).fetchall()


app = Flask(__name__)


@app.route("/<token>/")
def index(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    answers = get_list(token)
    return render_template("index.html", attempts_left=MAX_ATTEMPTS - len(get_list(token)), flag=get_flag(token) if ANSWER in answers else None)


@app.route("/<token>/attempts_left")
def attempts_left(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    return str(MAX_ATTEMPTS - len(get_list(token)))


@app.route("/<token>/submit", methods=["POST"])
def submit(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    try:
        x = int(request.form["x"])
        z = int(request.form["z"])
    except (KeyError, ValueError):
        return "Please fill the form correctly.", 400

    answers = get_list(token)

    if (x, z) in answers:
        if (x, z) == ANSWER:
            # Always allow resubmitting correct answer to get a flag if lost
            return f"This is correct! Flag: {get_flag(token)}"
        else:
            return "You have already submitted these wrong coordinates before."

    if len(answers) >= MAX_ATTEMPTS:
        return "You're out of attempts, sorry."

    cur.execute("INSERT INTO submits(token, x, z) VALUES(?, ?, ?)", (token, x, z))

    if (x, z) == ANSWER:
        return f"This is correct! Flag: {get_flag(token)}"
    else:
        return "These are the wrong coordinates."
