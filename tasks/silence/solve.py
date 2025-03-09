import socket, sys, time

sock = socket.create_connection(("q.2025.ugractf.ru", 3252))
sock.settimeout(1)

while True:
    # Считываем, пока считывается
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                sys.exit(0)
            sys.stdout.buffer.write(bytes([len(data)]))
            sys.stdout.buffer.flush()
    except TimeoutError:
        pass

    # Отправляем ввод
    for c in (input() + "\n").encode():
        sock.send(b"\x00" * c)
        time.sleep(0.1)
