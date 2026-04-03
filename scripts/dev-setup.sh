#!/usr/bin/env bash
# Quick local dev setup script
set -euo pipefail

echo "=== Sozo Protocol Generator — Dev Setup ==="

# Start services
echo "Starting PostgreSQL and Redis..."
docker compose up -d db redis

# Wait for DB
echo "Waiting for database..."
until docker compose exec db pg_isready -U sozo > /dev/null 2>&1; do
    sleep 1
done

# Run migrations
echo "Running database migrations..."
docker compose run --rm migrate

# Install Python deps
echo "Installing Python dependencies..."
python3.11 -m pip install -r requirements.txt

# Install frontend deps
echo "Installing frontend dependencies..."
cd frontend && npm install && cd ..

echo ""
echo "=== Setup complete! ==="
echo "Start API:      PYTHONPATH=src python3.11 -m uvicorn sozo_api.server:app --reload --port 8000"
echo "Start frontend:  cd frontend && npm run dev"
echo "Start worker:    PYTHONPATH=src celery -A sozo_workers.app worker --loglevel=info"
echo "Or run all:      docker compose up"
