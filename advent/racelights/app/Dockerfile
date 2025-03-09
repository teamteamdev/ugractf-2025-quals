FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

ARG POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN pip install --no-cache poetry

COPY pyproject.toml poetry.lock /app/
COPY racelights/__init__.py /app/racelights/

RUN poetry install --only main

FROM python:3.12-slim-bookworm

RUN useradd -ms /bin/bash racelights
USER racelights

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv /app/.venv
COPY pyproject.toml poetry.lock /app/
COPY racelights /app/racelights

CMD ["racelights"]
