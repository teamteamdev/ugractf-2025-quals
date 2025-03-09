#!/usr/bin/env sh
trap 'pkill -P $$; exit 0' EXIT INT TERM

# Fix permission errors with $HOME/.cache
export HOME=/tmp

python3 simulator.py "$SERVICE_HOST" &

# Reap orphans
wait
