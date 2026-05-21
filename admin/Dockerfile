FROM ghcr.io/astral-sh/uv:0.11-python3.13-alpine@sha256:099503f2fe3e97d8b3c0bf972203a18594abf0f546599a04f457c658ee5b3943

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/usr/src/app/.venv/bin:$PATH"

WORKDIR /usr/src/app

COPY . .

RUN uv sync --frozen --no-install-project --group admin --no-group bot --no-group dev \
    && adduser -D appuser \
    && chown -R appuser:appuser .

USER appuser

CMD ["gunicorn", "-c", "admin/gunicorn_conf.py"]
