#!/usr/bin/env python3
"""Setup script for Correlation Heatmap System."""
import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, cwd=None, check=True, shell=False):
    """Run shell command."""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print(f"{'='*60}\n")
    
    if isinstance(cmd, str):
        shell = True
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell,
        check=check,
        capture_output=False
    )
    return result


def check_docker():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            check=False
        )
        if result.returncode != 0:
            print("Error: Docker is not running")
            print("\nPlease start Docker Desktop and try again.")
            print("On macOS: Open Docker Desktop application")
            print("On Linux: Run 'sudo systemctl start docker'")
            print("\nWaiting for Docker to start...")
            input("Press Enter after starting Docker, or Ctrl+C to exit...")
            
            # Check again
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                check=False
            )
            if result.returncode != 0:
                print("Error: Docker is still not running")
                return False
        return True
    except FileNotFoundError:
        print("Error: Docker is not installed")
        print("Please install Docker Desktop from https://www.docker.com/products/docker-desktop")
        return False


def start_services():
    """Start Docker services."""
    print("\n[1/5] Starting Docker services...")
    if not check_docker():
        sys.exit(1)
    
    backend_dir = Path(__file__).parent / "backend"
    run_command(
        ["docker-compose", "up", "-d"],
        cwd=backend_dir
    )
    
    print("\nWaiting for services to be ready...")
    time.sleep(10)
    print("Services started")


def run_migrations():
    """Run database migrations."""
    print("\n[2/5] Running database migrations...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Try different ways to run alembic
    commands = [
        ["alembic", "upgrade", "head"],
        ["python3", "-m", "alembic", "upgrade", "head"],
        ["python", "-m", "alembic", "upgrade", "head"],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                cwd=backend_dir,
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                print("Migrations completed")
                return
        except FileNotFoundError:
            continue
    
    # If all fail, try installing dependencies first
    print("Alembic not found, installing dependencies...")
    subprocess.run(
        ["pip", "install", "-q", "-r", "requirements.txt"],
        cwd=backend_dir,
        check=True
    )
    
    # Try again with python -m
    run_command(
        ["python3", "-m", "alembic", "upgrade", "head"],
        cwd=backend_dir
    )
    print("Migrations completed")


def start_backend():
    """Start backend server."""
    print("\n[3/5] Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if dependencies are installed
    venv_exists = (backend_dir / "venv").exists() or (backend_dir / ".venv").exists()
    if not venv_exists:
        print("Installing backend dependencies...")
        subprocess.run(
            ["pip", "install", "-q", "-r", "requirements.txt"],
            cwd=backend_dir,
            check=True
        )
    
    print("Starting uvicorn server (will run in background)...")
    
    # Try different ways to run uvicorn
    commands = [
        ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
    ]
    
    for cmd in commands:
        try:
            subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            break
        except FileNotFoundError:
            continue
    else:
        # If all fail, install and try again
        print("Uvicorn not found, installing dependencies...")
        subprocess.run(
            ["pip", "install", "-q", "-r", "requirements.txt"],
            cwd=backend_dir,
            check=True
        )
        subprocess.Popen(
            ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print("Backend server starting at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    time.sleep(3)


def install_frontend_deps():
    """Install frontend dependencies."""
    print("\n[4/5] Installing frontend dependencies...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not (frontend_dir / "node_modules").exists():
        run_command(
            ["npm", "install"],
            cwd=frontend_dir
        )
    else:
        print("Frontend dependencies already installed, skipping...")


def start_frontend():
    """Start frontend dev server."""
    print("\n[5/5] Starting frontend dev server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    print("Starting Vite dev server...")
    print("Frontend will be available at http://localhost:5173")
    print("\n" + "="*60)
    print("Setup complete! Services are running.")
    print("="*60)
    print("\nBackend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services\n")
    
    run_command(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )


def main():
    """Main setup function."""
    print("="*60)
    print("Correlation Heatmap System - Setup Script")
    print("="*60)
    
    try:
        start_services()
        run_migrations()
        start_backend()
        install_frontend_deps()
        start_frontend()
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        backend_dir = Path(__file__).parent / "backend"
        run_command(
            ["docker-compose", "down"],
            cwd=backend_dir,
            check=False
        )
        print("Services stopped")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()

