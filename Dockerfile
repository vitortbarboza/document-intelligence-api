
# Use a lightweight Python 3.13 image.
FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffer-free logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container.
WORKDIR /app

# Copy project metadata and application source.
COPY pyproject.toml ./
COPY app/ ./app/

# Copy Alembic configuration and database migrations.
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Install the application and its runtime dependencies.
RUN pip install --no-cache-dir .

# Create a directory for persistent application data.
RUN mkdir -p /data

# Configure the SQLite database location.
ENV DATABASE_URL=sqlite:////data/documents.db

# Document the port used by the API.
EXPOSE 8000

# Apply database migrations before starting the API.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]