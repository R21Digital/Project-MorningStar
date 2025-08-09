# Multi-stage Dockerfile for MS11 Production Deployment
# Stage 1: Base Python environment with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    redis-tools \
    tesseract-ocr \
    libtesseract-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxrandr-dev \
    libxtst-dev \
    libxi-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r ms11 && useradd -r -g ms11 ms11

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements/ ./requirements/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Development environment
FROM base as development

# Install development dependencies
RUN pip install -r requirements/dev.txt

# Copy source code
COPY . .

# Change ownership to app user
RUN chown -R ms11:ms11 /app

# Create necessary directories
RUN mkdir -p logs data/sessions profiles/runtime backups && \
    chown -R ms11:ms11 logs data profiles backups

USER ms11

# Expose ports
EXPOSE 5000 8080

# Development command
CMD ["python", "src/main.py", "--dev"]

# Stage 3: Production environment
FROM base as production

# Install production dependencies only
RUN if [ -f requirements/production.txt ]; then \
        pip install -r requirements/production.txt; \
    fi

# Copy only necessary files for production
COPY src/ ./src/
COPY core/ ./core/
COPY modules/ ./modules/
COPY dashboard/ ./dashboard/
COPY config/ ./config/
COPY migrations/ ./migrations/
COPY data/ ./data/
COPY scripts/entrypoint.sh ./scripts/
COPY scripts/healthcheck.sh ./scripts/

# Make scripts executable
RUN chmod +x ./scripts/entrypoint.sh ./scripts/healthcheck.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/backups /app/profiles/runtime && \
    chown -R ms11:ms11 /app

# Switch to non-root user
USER ms11

# Expose ports
EXPOSE 5000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ./scripts/healthcheck.sh

# Default production command
ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD ["python", "src/main.py", "--prod"]

# Stage 4: Testing environment
FROM base as testing

# Install test dependencies
RUN pip install -r requirements/dev.txt

# Copy source code
COPY . .

# Change ownership
RUN chown -R ms11:ms11 /app

USER ms11

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v"]
