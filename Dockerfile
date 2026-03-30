FROM python:3.13-slim

WORKDIR /app

# Install UV from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock ./

# Install only runtime dependencies inside the container
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY src ./src
COPY models ./models

# Make the UV virtual environment available
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "src.api.app:app"]
