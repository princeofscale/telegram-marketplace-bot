FROM ghcr.io/astral-sh/uv:0.11-python3.13-alpine@sha256:396b9430122ad5bb166339156a02f54025e152409297c260072fe78ae5b641fe

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
