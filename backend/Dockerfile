FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with optimization
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel for faster builds
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy application code
COPY . .

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Create directories for SQLite and logs
RUN mkdir -p /app/data /app/logs && chmod 755 /app/data /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]