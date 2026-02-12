#!/bin/sh
# Start script for production deployment

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the server
# Use PORT from environment, default to 8000
PORT="${PORT:-8000}"
echo "Starting server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
