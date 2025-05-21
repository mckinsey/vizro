FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev --no-editable

COPY . /app

ENTRYPOINT ["uv", "run", "vizro-mcp"]
