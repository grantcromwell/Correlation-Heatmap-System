#!/bin/bash
# Setup script for Correlation Heatmap System (without Docker)
# Use this if you have PostgreSQL, Redis, and Temporal running separately

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "============================================================"
echo "Correlation Heatmap System - Setup (No Docker)"
echo "============================================================"
echo ""
echo "This script assumes you have PostgreSQL, Redis, and Temporal"
echo "running separately. Make sure they're configured in backend/.env"
echo ""

read -p "Press Enter to continue or Ctrl+C to exit..."

# 1. Run migrations
echo ""
echo "[1/4] Running database migrations..."
cd "$BACKEND_DIR"
alembic upgrade head
echo "Migrations completed"

# 2. Start backend
echo ""
echo "[2/4] Starting backend server..."
cd "$BACKEND_DIR"
echo "Starting uvicorn server in background..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo "Backend server starting at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
sleep 3

# 3. Install frontend dependencies
echo ""
echo "[3/4] Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Frontend dependencies already installed, skipping..."
fi

# 4. Start frontend
echo ""
echo "[4/4] Starting frontend dev server..."
echo "============================================================"
echo "Setup complete! Services are running."
echo "============================================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop services"
echo ""

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null; exit" INT

# Start frontend (this will block)
npm run dev

