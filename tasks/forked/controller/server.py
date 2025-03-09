from kyzylborda_lib.sandbox import start_oneshot
from kyzylborda_lib.secrets import validate_token, get_secret, get_flag
from kyzylborda_lib.server import tcp


@tcp.listen
async def handle(conn: tcp.Connection):
    await conn.writeall(b"Enter token: ")
    token = (await conn.readline()).decode(errors="ignore").strip()
    if not validate_token(token):
        await conn.writeall(b"Wrong token\n")
        return
    box = await start_oneshot(token)
    with box.open(get_secret("flag-path", token), "w") as f:
        f.write(get_flag(token))
    return box
