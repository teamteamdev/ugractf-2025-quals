from kyzylborda_lib.sandbox import start_box
from kyzylborda_lib.secrets import validate_token
from kyzylborda_lib.server import tcp


@tcp.listen
async def handle(conn: tcp.Connection):
    try:
        method, rest = (await conn.readline()).split(None, 1)
    except ValueError:
        return
    if not rest or rest[0] != 47:
        await conn.writeall(b"HTTP/1.1 400\n\nMalformed request\n")
        return

    rest = rest.rstrip(b'\r\n')
    if (rest.endswith(b"HTTP/1.0") or rest.endswith(b"HTTP/1.1")) and len(rest) > 8 and rest[-9:][:1].isspace():
        rest = rest[:-8].rstrip()
    elif rest.endswith(b"HTTP/2") and len(rest) >= 6 and rest[-7:][:1].isspace():
        rest = rest[:-6].rstrip()

    rest = rest[1:]
    pos = rest.find(b'/')
    if pos == -1:
        pos = len(rest)
        rest += b'/'

    raw_token, rest = rest[:pos], rest[pos:]
    if not raw_token:
        await conn.writeall(b"HTTP/1.1 401\n\nToken required\n")
        return

    token = raw_token.decode(errors='replace')
    if not validate_token(token):
        await conn.writeall(b"HTTP/1.1 400\n\nWrong token\n")
        return

    for tok in [method, b' ', rest, b' HTTP/1.1\nX-Token: ', raw_token, b'\n'][::-1]:
        conn.unread(tok)

    return await start_box(token, pass_secrets=["flag"])
