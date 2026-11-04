
# Use a lightweight Python 3.13 image.
FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffer-free logs.
# uv must use the image's Python and copy files out of its cache mount.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy

# Set the working directory inside the container.
WORKDIR /app

# Install only the locked runtime dependencies. This layer is rebuilt only
# when pyproject.toml or uv.lock change, not on every source code change.
# uv is mounted for this step only, so it is not part of the final image.
COPY pyproject.toml uv.lock ./
RUN --mount=from=ghcr.io/astral-sh/uv:0.12.20,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# Run the application from the source tree instead of installing it again
# into the virtual environment.
ENV PATH="/app/.venv/bin:$PATH"

# Copy Alembic configuration and database migrations.
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Copy the application source.
COPY app/ ./app/

# Create an unprivileged user that owns the persistent data directory.
# The fixed UID makes volume ownership predictable across rebuilds.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home app \
    && mkdir -p /data \
    && chown app:app /data

# Configure the SQLite database location.
ENV DATABASE_URL=sqlite:////data/documents.db

USER app

# Document the port used by the API.
EXPOSE 8000

# Report the container as unhealthy when the API stops answering.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --start-interval=2s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

# Apply database migrations before starting the API.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
