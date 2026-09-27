FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

RUN uv sync --frozen --no-dev

EXPOSE 8000

<<<<<<< HEAD
CMD ["uv", "run", "uvicorn", "brave_abroad.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
CMD ["uv", "run", "uvicorn", "brave_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> BRAVE-003
