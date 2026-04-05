# LIDA Docker Configuration
# Multi-stage build for optimized production image

# === Base stage ===
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# === Dependencies stage ===
FROM base AS dependencies

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY requirements.txt pyproject.toml* ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[web]"

# === Production stage ===
FROM base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY lida/ ./lida/
COPY README.md LICENSE ./

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Run the application
CMD ["lida", "ui", "--host", "0.0.0.0", "--port", "8080"]
