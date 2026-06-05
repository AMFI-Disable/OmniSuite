FROM python:3.9-slim

# Copy uv package manager binaries from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment configurations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install system dependencies (build-essential for python-docx or libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv workspace definitions and packages source
COPY pyproject.toml /app/
COPY src /app/src

# Synchronize python virtualenv and dependencies using uv
RUN uv venv /app/.venv && uv sync --all-packages

# Copy launcher, configs, and directory structures
COPY omnisuite /app/
COPY config /app/config
COPY data /app/data

# Ensure launcher is executable
RUN chmod +x /app/omnisuite

# Define default entrypoint to support passing launcher options directly
ENTRYPOINT ["python3", "omnisuite"]
