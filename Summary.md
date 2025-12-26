# Project Summary

## Overview

The Correlation Heatmap System is a full-stack financial analysis platform designed to discover, analyze, and visualize correlations across multiple asset classes. The system enables quantitative analysis of market relationships through correlation calculations, backtesting, and interactive visualizations.

## Technical Architecture

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **Cache**: Redis for data caching and session management
- **Workflow Engine**: Temporal for distributed workflow orchestration
- **Data Sources**: Alpha Vantage API, Finnhub API, yfinance library

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS for responsive design
- **State Management**: TanStack Query for server state management
- **Real-time Communication**: WebSocket support

## Core Features

1. **Correlation Analysis**
   - Calculate Pearson correlation coefficients between instrument pairs
   - Support for multiple asset classes (equities, cryptocurrencies, forex)
   - Statistical significance testing with p-values

2. **Backtesting Engine**
   - Multiple trading strategies: pairs trading, momentum, mean reversion
   - Performance metrics: Sharpe ratio, maximum drawdown, win rate
   - Historical data analysis with configurable timeframes

3. **Visualization**
   - Interactive correlation heatmaps
   - Real-time updates via WebSocket
   - Export capabilities for further analysis

4. **Advanced Features**
   - H3 geospatial indexing for correlation clustering
   - Decoupling detection algorithms
   - Spanning tree analysis for correlation networks

## Development Practices

- Type safety with TypeScript (frontend) and type hints (backend)
- Comprehensive testing framework setup
- Code quality tools: ESLint, Prettier, Ruff, MyPy
- Database migrations with Alembic
- Docker Compose for local development
- CI/CD workflow configuration

## Learning Outcomes

This project demonstrates:
- Full-stack development skills
- API design and integration
- Database design and optimization
- Real-time data processing
- Financial data analysis
- Software engineering best practices

