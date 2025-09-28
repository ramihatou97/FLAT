# =============================================================================
# Medical Knowledge Platform - Production Docker Image
# =============================================================================
# Multi-stage build for optimized production deployment
# Supports latest AI providers: Gemini 2.5 Pro, Claude Opus 4.1, OpenAI, Perplexity
# =============================================================================

# Build stage
FROM python:3.11-slim as builder

# Set build environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements/ /tmp/requirements/
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set production environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directories
WORKDIR /app
RUN mkdir -p logs uploads reference_library data/embeddings backups

# Create non-root user with specific UID for security
RUN groupadd -r -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup -d /app -s /bin/bash app

# Copy application code
COPY --chown=app:appgroup . .

# Set proper permissions
RUN chown -R app:appgroup /app && \
    chmod -R 755 /app && \
    chmod 700 data/ && \
    chmod 755 logs uploads reference_library

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Add health check with proper timeout
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Use gunicorn for production with proper worker configuration
CMD ["gunicorn", "simple_main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "300", \
     "--keepalive", "2", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]