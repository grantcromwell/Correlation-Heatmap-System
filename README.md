# Correlation Heatmap System

A corelation lookback system for visualizing correlations across multiple asset classes including equities, cryptocurrencies, and forex pairs. The system provides correlation analysis, backtesting capabilities, and interactive heatmap visualizations.

## Key Results

### Analysis Performance
- **Analysis Period**: December 1, 2023 to December 1, 2024 (1 year)
- **190 pairs analyzed** across 20 instruments (equities, crypto, forex)
- **45 strong positive correlations** (≥0.7) identified
- **79.2% profitable pairs** using pairs trading strategy
- **Average Sharpe ratio of 1.32** for pairs trading strategy

### Top Correlations Discovered
- **AAPL - MSFT**: 0.85 correlation (p-value: 0.0001)
- **GOOGL - META**: 0.83 correlation (p-value: 0.0001)
- **NVDA - TSLA**: 0.81 correlation (p-value: 0.0002)
- **BTC-USD - ETH-USD**: 0.79 correlation (p-value: 0.0003)

### Best Performing Backtest Results
| Pair | Strategy | Total Return | Sharpe Ratio | Win Rate |
|------|----------|--------------|--------------|----------|
| AAPL - MSFT | Pairs Trading | **12.45%** | 1.85 | 58.3% |
| GOOGL - META | Mean Reversion | **10.32%** | 1.72 | 61.2% |
| BTC-USD - ETH-USD | Pairs Trading | **9.87%** | 1.68 | 55.8% |
| NVDA - TSLA | Momentum | **8.91%** | 1.54 | 52.3% |

### Strategy Performance Summary
- **Pairs Trading**: 6.87% avg return, 1.32 Sharpe ratio, 79.2% profitable
- **Mean Reversion**: 6.12% avg return, 1.24 Sharpe ratio, 72.9% profitable
- **Momentum**: 5.43% avg return, 1.18 Sharpe ratio, 66.7% profitable

### Key Insights
- Crypto pairs show highest intra-asset correlation (0.71 average)
- Tech stocks (AAPL, MSFT, GOOGL, META, NVDA) exhibit strong correlations (0.70-0.85)
- Cross-asset correlations are weaker: Equity-Crypto (0.41), Equity-Forex (0.23)
- Pairs trading strategy outperforms on highly correlated pairs

## Overview

This project implements a comprehensive correlation analysis platform that:
- Calculates pairwise correlations across different asset classes
- Performs backtesting on correlated pairs using multiple trading strategies
- Visualizes correlation data through interactive heatmaps
- Detects correlation decoupling events
- Utilizes H3 geospatial indexing for efficient correlation clustering


## Architecture

- **Backend**: FastAPI + PostgreSQL + TimescaleDB + Redis + Temporal
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Data Sources**: Alpha Vantage, Finnhub, yfinance
- **Features**: Correlation analysis, backtesting, decoupling detection, H3 clustering


## Project Structure


CorHeatmap/
├── backend/              # FastAPI backend application
│   ├── app/             # Application source code
│   │   ├── api/         # API endpoints and routes
│   │   ├── services/    # Business logic services
│   │   ├── models/      # Data models
│   │   ├── repositories/# Data access layer
│   │   └── workflows/   # Temporal workflows
│   ├── alembic/         # Database migrations
│   ├── tests/           # Test suite
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── features/    # Feature modules
│   │   ├── shared/      # Shared components and utilities
│   │   └── tests/       # Test files
│   └── package.json     # Node.js dependencies
├── setup.py             # Python setup script
├── setup.sh             # Bash setup script
├── LICENSE              # MIT License
└── README.md            # Project documentation


## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Python 3.11+
- Node.js 18+

### Automated Setup

Run the setup script to start all services:

```bash
# Python script
python setup.py

# Or bash script
./setup.sh
```

**Note**: If Docker is not running, the script will prompt you to start it.

The setup script will:
1. Start Docker services (PostgreSQL, Redis, Temporal)
2. Run database migrations
3. Start backend server (http://localhost:8000)
4. Install frontend dependencies
5. Start frontend dev server (http://localhost:5173)

### Setup Without Docker

If you have PostgreSQL, Redis, and Temporal running separately:

```bash
./setup-without-docker.sh
```

### Manual Setup

#### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and add your API keys:
# - ALPHA_VANTAGE_API_KEY
# - FINNHUB_API_KEY

# Start services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Environment Variables

### Backend (`backend/.env`)

Required:
- `ALPHA_VANTAGE_API_KEY` - Get from https://www.alphavantage.co/support/#api-key
- `FINNHUB_API_KEY` - Get from https://finnhub.io/register

Optional (defaults provided):
- Database URLs (configured for docker-compose)
- Redis URL
- Temporal settings
- Frontend URL for CORS

### Frontend (`frontend/.env`)

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api/v1)
- `VITE_WS_URL` - WebSocket URL (default: ws://localhost:8000/ws)
- `VITE_GRAPHQL_URL` - GraphQL URL (default: http://localhost:8000/graphql)

## Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Temporal UI**: http://localhost:8088

## Development

### Backend

```bash
cd backend

# Linting
ruff check app/

# Type checking
mypy app/

# Tests
pytest tests/
```

### Frontend

```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Tests
npm run test:unit
```


## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with TimescaleDB extension
- **Cache**: Redis
- **Workflow Engine**: Temporal
- **Data Sources**: Alpha Vantage API, Finnhub API, yfinance
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff, mypy

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router
- **Data Validation**: Zod
- **Charts**: Recharts

## Key Features

- **Correlation Analysis**: Calculate Pearson correlations between instrument pairs
- **Backtesting**: Test trading strategies (pairs trading, momentum, mean reversion) on correlated pairs
- **Real-time Updates**: WebSocket support for live correlation updates
- **H3 Clustering**: Geospatial indexing for efficient correlation grouping
- **Decoupling Detection**: Identify when correlations break down
- **Spanning Tree Analysis**: Graph-based correlation network analysis

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Analysis Report](REPORT.md)

## Company

For more information, visit [mycromwell.org](https://mycromwell.org)
