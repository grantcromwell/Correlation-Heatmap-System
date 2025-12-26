# Correlation Heatmap Backend

Backend API for the Correlation Heatmap System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file with your API keys:
```bash
# Edit backend/.env and add your API keys:
# - ALPHA_VANTAGE_API_KEY (get from https://www.alphavantage.co/support/#api-key)
# - FINNHUB_API_KEY (get from https://finnhub.io/register)
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Linting
```bash
ruff check backend/
```

### Type Checking
```bash
mypy backend/app/
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

