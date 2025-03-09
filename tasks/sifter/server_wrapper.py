from kyzylborda_lib.secrets import get_flag, validate_token
from kyzylborda_lib.server import http
import subprocess


@http.listen
async def handle(req: http.Request):
    token = req.path[1:]
    if validate_token(token):
        return http.respond(200, get_flag(token).encode())
    else:
        return http.respond(403, b"")


_ = subprocess.Popen("/controller")
