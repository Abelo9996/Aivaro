# API Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port (can be overridden by environment)
ENV PORT=8000
EXPOSE 8000

# Run migrations and start server
CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}"
