from flask import abort, Flask, Response, send_file, send_from_directory
from kyzylborda_lib.secrets import get_flag, validate_token
from mimetypes import guess_file_type
from typing import Optional
import unicodedata
from werkzeug.security import safe_join


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    with open("/out/404.html", "rb") as f:
        data = f.read()
    data = data.replace(b"KYZYLBORDA_TOKEN", b"_")
    return data, 404


@app.route("/<token>/")
@app.route("/<token>/<path:path>")
def list(token: str, path: Optional[str] = None):
    if token != "_" and not validate_token(token):
        return "Invalid token.", 401

    path = safe_join("/out", path or "index.html")
    try:
        if path is None:
            raise FileNotFoundError()
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        abort(404)

    data = data.replace(b"KYZYLBORDA_TOKEN", token.encode())
    if b"KYZYLBORDA_FLAG" in data:
        flag = "No flag here -- did you forget the token?" if token == "_" else "\\n".join(unicodedata.name(char) for char in get_flag(token))
        data = data.replace(b"KYZYLBORDA_FLAG", flag.encode())

    return Response(
        data,
        content_type=guess_file_type(path or "index.html")[0] or "application/octet-stream",
    )
