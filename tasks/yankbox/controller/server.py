from kyzylborda_lib.sandbox import start_box
from kyzylborda_lib.secrets import get_flag, validate_token
from kyzylborda_lib.server import http


def init(box):
    with box.open("/flag.txt", "w+") as f:
        f.write(get_flag(box.token))


@http.listen
async def handle(req: http.Request):
    if not req.path or req.path[0] != '/':
        return http.respond(400, b"Malformed request\n")
    req.path = req.path[1:]
    pos = req.path.find('/')
    if pos == -1:
        pos = len(req.path)
        req.path += '/'
    token, req.path = req.path[:pos], req.path[pos:]
    if not token:
        return http.respond(401, b"Token required\n")
    if not validate_token(token):
        return http.respond(400, b"Wrong token\n")
    req.headers["X-Token"] = token
    return await start_box(token, init=init)
