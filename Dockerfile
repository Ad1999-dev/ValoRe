# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies needed for building some ML packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a virtual environment
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime
# Using 3.11-slim as it is more stable for current ML libraries than 3.13
FROM python:3.11-slim
WORKDIR /app

# Install libgomp1 (MANDATORY for XGBoost to run on Linux)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code and required assets
COPY src ./src
COPY templates ./templates

# Use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# FastAPI usually runs on 8080 for Cloud Run
EXPOSE 8080

# Use Uvicorn for FastAPI performance
# We use --workers 1 to keep memory usage low when loading large models
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
