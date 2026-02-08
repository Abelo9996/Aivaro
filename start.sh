#!/bin/bash

# Aivaro Quick Start Script
# Run this to set up and start the project

echo "🚀 Starting Aivaro Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Copy environment file if not exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Start PostgreSQL
echo "🐘 Starting PostgreSQL..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Set up API
echo "🐍 Setting up API..."
cd api

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -r requirements.txt -q

# Run migrations
echo "  Running database migrations..."
alembic upgrade head

# Seed templates
echo "  Seeding templates..."
python -c "from app.seed.templates import seed_templates; from app.database import SessionLocal; db = SessionLocal(); seed_templates(db); db.close()"

# Start API in background
echo "  Starting API server..."
python run.py &
API_PID=$!

cd ..

# Set up Web
echo "🌐 Setting up Web..."
cd web

# Install dependencies
echo "  Installing Node dependencies..."
npm install

# Start web in background
echo "  Starting Next.js dev server..."
npm run dev &
WEB_PID=$!

cd ..

echo ""
echo "✅ Aivaro is starting up!"
echo ""
echo "📍 API: http://localhost:8000"
echo "📍 Web: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $API_PID $WEB_PID 2>/dev/null; docker-compose down; exit 0" INT
wait
