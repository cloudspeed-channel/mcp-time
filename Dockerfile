# syntax=docker/dockerfile:1.4
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

WORKDIR /app

ENV UV_PYTHON=python3.12
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV LOCAL_TIMEZONE=UTC
ENV PATH="/app/.venv/bin:$PATH"

# Copy project metadata
COPY pyproject.toml ./

# Instead of relying on a stale lock, generate a new one inside the container
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --no-editable

# Copy project source and install it
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable

RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "-m", "mcp_server_time"]
