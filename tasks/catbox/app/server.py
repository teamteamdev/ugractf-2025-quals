from datetime import datetime
from flask import Flask, render_template, request, send_file
from kyzylborda_lib.secrets import validate_token
from mimetypes import guess_file_type
import os
import sqlite3
from tempfile import NamedTemporaryFile
import time


SERVICE_NAME = "Catbox" if os.environ["TASK_NAME"] == "catbox" else "Boxcat"


con = sqlite3.connect("/state/uploads.db", autocommit=True)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS uploads(token TEXT, id TEXT, password TEXT, file_name TEXT, date_uploaded INTEGER, path TEXT)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uploads_token_id ON uploads(token, id)")

os.makedirs("/state/uploads", exist_ok=True)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024


@app.route("/<token>/")
def list(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    uploads = [
        {
            "id": id,
            "file_name": file_name,
            "date_uploaded": datetime.fromtimestamp(date_uploaded).isoformat(),
        }
        for id, file_name, date_uploaded
        in cur.execute("SELECT id, file_name, date_uploaded FROM uploads WHERE token = ? ORDER BY date_uploaded DESC", (token,))
    ]
    return render_template("list.html", uploads=uploads, service_name=SERVICE_NAME)


@app.route("/<token>/what-is-a-cat/")
def what_is_a_cat(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    return render_template("what_is_a_cat.html", service_name=SERVICE_NAME)


@app.route("/<token>/upload/", methods=["GET"])
def upload_ui(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    return render_template("upload.html", service_name=SERVICE_NAME)


@app.route("/<token>/upload/", methods=["POST"])
def upload_action(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    id = request.form["id"]
    password = request.form["password"]
    file = request.files["file"]

    with NamedTemporaryFile(dir="/state/uploads", delete=False) as f:
        request.files["file"].save(f)

    try:
        cur.execute(
            "INSERT INTO uploads(token, id, password, file_name, date_uploaded, path) VALUES (?, ?, ?, ?, ?, ?)",
            (token, id, password, file.filename, int(time.time()), f.name),
        )
    except sqlite3.IntegrityError as e:
        return render_template("upload_conflict.html", id=id, file_name=file.filename, service_name=SERVICE_NAME), 409

    return render_template("uploaded.html", id=id, password=password, file_name=file.filename, service_name=SERVICE_NAME)


@app.route("/<token>/view/<id>/")
def view(token: str, id: str):
    if not validate_token(token):
        return "Invalid token.", 401

    row = cur.execute(
        "SELECT file_name, password, date_uploaded, path FROM uploads WHERE token = ? AND id = ?",
        (token, id),
    ).fetchone()

    if row:
        file_name, password, date_uploaded, path = row
        req_password = request.args.get("password")
        if req_password == password:
            return send_file(
                path,
                mimetype=guess_file_type(file_name)[0] or "application/octet-stream",
                as_attachment=True,
                download_name=file_name,
                conditional=True,
                etag=True,
                last_modified=date_uploaded,
            )
        else:
            return render_template("view.html", file_name=file_name, wrong_password=req_password is not None, service_name=SERVICE_NAME)
    else:
        return render_template("file_not_found.html", service_name=SERVICE_NAME), 404
