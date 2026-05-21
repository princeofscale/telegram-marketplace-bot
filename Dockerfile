FROM ghcr.io/astral-sh/uv:0.11-python3.13-alpine

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/usr/src/app/.venv/bin:$PATH"

WORKDIR /usr/src/app

COPY . .

RUN uv sync --frozen --no-install-project --group bot --no-group admin --no-group dev \
    && pybabel compile -d ./bot/locales \
    && adduser -D appuser \
    && chown -R appuser:appuser .

USER appuser

CMD ["python", "-m", "bot"]
