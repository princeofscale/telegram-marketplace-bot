FROM ghcr.io/astral-sh/uv:0.12-python3.13-alpine@sha256:31a524210097e4f2d6f732d525cf9479c02ec966a0cd13f43ef71650ef3abf72

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
