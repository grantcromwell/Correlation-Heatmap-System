#!/bin/bash
# Setup script for Correlation Heatmap System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "============================================================"
echo "Correlation Heatmap System - Setup Script"
echo "============================================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "Error: Docker is not running"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo "On macOS: Open Docker Desktop application"
    echo "On Linux: Run 'sudo systemctl start docker'"
    echo ""
    read -p "Press Enter after starting Docker, or Ctrl+C to exit..."
    
    # Check again after waiting
    if ! docker ps &> /dev/null; then
        echo "Error: Docker is still not running"
        exit 1
    fi
fi

# 1. Start Docker services
echo ""
echo "[1/5] Starting Docker services..."
cd "$BACKEND_DIR"
docker-compose up -d
echo "Waiting for services to be ready..."
sleep 10
echo "Services started"

# 2. Setup Python virtual environment
echo ""
echo "[2/6] Setting up Python virtual environment..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    
    # Try to find Python 3.11 or 3.12 first (more compatible)
    if command -v python3.12 &> /dev/null; then
        echo "Using Python 3.12"
        python3.12 -m venv venv
    elif command -v python3.11 &> /dev/null; then
        echo "Using Python 3.11"
        python3.11 -m venv venv
    elif command -v python3.13 &> /dev/null; then
        echo "Using Python 3.13"
        python3.13 -m venv venv
    else
        echo "Using default Python 3"
        python3 -m venv venv || python -m venv venv
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies if needed
if ! python -m alembic --help &> /dev/null 2>&1; then
    echo "Installing backend dependencies..."
    pip install -q -r requirements.txt
fi

# 3. Run migrations
echo ""
echo "[3/6] Running database migrations..."
python -m alembic upgrade head || python3 -m alembic upgrade head
echo "Migrations completed"

# 4. Start backend
echo ""
echo "[4/6] Starting backend server..."
cd "$BACKEND_DIR"

# Ensure venv is activated
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Starting uvicorn server in background..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

BACKEND_PID=$!
echo "Backend server starting at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
sleep 3

# 5. Install frontend dependencies
echo ""
echo "[5/6] Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Frontend dependencies already installed, skipping..."
fi

# 6. Start frontend
echo ""
echo "[6/6] Starting frontend dev server..."
echo "============================================================"
echo "Setup complete! Services are running."
echo "============================================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping services...'; docker-compose -f $BACKEND_DIR/docker-compose.yml down; kill $BACKEND_PID 2>/dev/null; exit" INT

# Start frontend (this will block)
npm run dev

