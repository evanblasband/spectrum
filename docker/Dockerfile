# Spectrum - Political News Analyzer
# Multi-stage Dockerfile for production and development

# ===================
# Base stage
# ===================
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies for lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===================
# Production stage
# ===================
FROM base as production

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===================
# Development stage
# ===================
FROM base as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

ENV PYTHONUNBUFFERED=1
ENV DEBUG=true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
