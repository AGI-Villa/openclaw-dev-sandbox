# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install poetry and dependencies
RUN pip install poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --only=main

# Runtime stage
FROM python:3.10-slim AS runtime

WORKDIR /app

# Install system dependencies for rembg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy built application and dependencies
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Default command for CLI
CMD ["bg-remove", "--help"]

# Web server command
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["bg_removal.web:app", "--host", "0.0.0.0", "--port", "8080"]