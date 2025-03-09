#!/bin/sh
set -e

[ -f /tmp/constructor.db ] || python3 init.py

# sqlmap hangs with a single worker
gunicorn -w 16 -b unix:/tmp/app.sock server:app
