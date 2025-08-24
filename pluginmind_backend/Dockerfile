# PluginMind Backend - Production Docker Configuration
# Multi-stage build for optimized production deployment

# =============================================================================
# Base Python image with shared dependencies
# =============================================================================
FROM python:3.12-alpine as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for Python packages
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    curl \
    gcc \
    musl-dev \
    libffi-dev

# Create app user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set work directory
WORKDIR /app

# =============================================================================
# Dependencies stage - for efficient layer caching
# =============================================================================
FROM base as dependencies

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Development stage - includes dev tools and source mounting capability
# =============================================================================
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio httpx

# Copy application source
COPY . .

# Change ownership to app user
RUN chown -R appuser:appgroup /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default development command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production stage - optimized, minimal, secure
# =============================================================================
FROM dependencies as production

# Copy only necessary application files
COPY app/ ./app/
COPY gunicorn_conf.py .
COPY scripts/ ./scripts/

# Create necessary directories for production
RUN mkdir -p /app/logs /app/tmp && \
    chmod 755 /app/scripts/smoke_backend.sh /app/scripts/smoke_errors.sh

# Change ownership to app user
RUN chown -R appuser:appgroup /app

# Switch to non-root user for security
USER appuser

# Expose port
EXPOSE 8000

# Health check for production
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ready || exit 1

# Production command using Gunicorn
CMD ["gunicorn", "app.main:app", "--config", "gunicorn_conf.py"]

# =============================================================================
# Test stage - for CI/CD testing
# =============================================================================
FROM dependencies as testing

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio httpx coverage

# Copy all source files for testing
COPY . .

# Change ownership
RUN chown -R appuser:appgroup /app

# Switch to app user
USER appuser

# Default test command
CMD ["python", "-m", "pytest", "-v", "--tb=short"]