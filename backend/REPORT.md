# Correlation Analysis & Backtesting Report

**Analysis Period**: 2024-12-26 to 2025-12-26
**Total Instruments Analyzed**: 20
**Total Pairs Analyzed**: 90

---

## Executive Summary

- **Strong Positive Correlations (≥0.7)**: 8 pairs
- **Strong Negative Correlations (≤-0.7)**: 0 pairs
- **Moderate Correlations (0.5-0.7)**: 29 pairs
- **Weak Correlations (<0.5)**: 53 pairs

---

## Top Correlations

### Strongest Positive Correlations

| Pair | Correlation | P-Value |
|------|-------------|---------|
| BTC-USD - ETH-USD | 0.8178 | 0.0000 |
| EURUSD=X - GBPUSD=X | 0.8009 | 0.0000 |
| BTC-USD - SOL-USD | 0.7978 | 0.0000 |
| ETH-USD - SOL-USD | 0.7921 | 0.0000 |
| SOL-USD - ADA-USD | 0.7653 | 0.0000 |
| BTC-USD - ADA-USD | 0.7489 | 0.0000 |
| ETH-USD - ADA-USD | 0.7472 | 0.0000 |
| ETH-USD - BNB-USD | 0.7017 | 0.0000 |

### Strongest Negative Correlations

| Pair | Correlation | P-Value |
|------|-------------|---------|

---

## Backtest Results

Backtests were run on 8 pairs with |correlation| ≥ 0.7 using three strategies:

1. **Pairs Trading**: Mean reversion strategy based on spread z-scores
2. **Momentum**: Trend-following strategy based on momentum signals
3. **Mean Reversion**: Mean reversion strategy with rolling statistics

### Best Performing Strategies

| Pair | Strategy | Total Return | Sharpe Ratio | Max Drawdown | Win Rate | Trades |
|------|----------|--------------|--------------|--------------|----------|--------|
| ETH-USD-BNB-USD | momentum | 38.86% | 0.97 | -20.60% | 17.26% | 42 |
| EURUSD=X-GBPUSD=X | mean_reversion | 2.36% | 0.84 | -1.89% | 14.01% | 51 |
| EURUSD=X-GBPUSD=X | momentum | 4.16% | 0.80 | -3.60% | 26.46% | 33 |
| BTC-USD-ETH-USD | momentum | 6.45% | 0.31 | -24.96% | 13.15% | 44 |
| ETH-USD-SOL-USD | momentum | 6.54% | 0.29 | -38.26% | 13.97% | 36 |
| ETH-USD-ADA-USD | momentum | 4.26% | 0.24 | -37.10% | 12.05% | 22 |
| BTC-USD-ETH-USD | mean_reversion | 0.43% | 0.12 | -30.70% | 11.51% | 64 |
| BTC-USD-SOL-USD | momentum | -1.52% | 0.07 | -29.94% | 15.62% | 24 |
| SOL-USD-ADA-USD | mean_reversion | -3.49% | 0.07 | -27.94% | 13.97% | 73 |
| BTC-USD-ETH-USD | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 2 |
| EURUSD=X-GBPUSD=X | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 0 |
| BTC-USD-SOL-USD | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 2 |
| ETH-USD-SOL-USD | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 2 |
| SOL-USD-ADA-USD | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 4 |
| BTC-USD-ADA-USD | pairs_trading | 0.00% | 0.00 | nan% | 0.00% | 2 |

### Strategy Performance Summary

#### Pairs Trading

- **Average Sharpe Ratio**: 0.00
- **Average Total Return**: 0.00%
- **Profitable Pairs**: 0/8 (0.0%)

#### Momentum

- **Average Sharpe Ratio**: 0.31
- **Average Total Return**: 5.31%
- **Profitable Pairs**: 5/8 (62.5%)

#### Mean Reversion

- **Average Sharpe Ratio**: -0.55
- **Average Total Return**: -29.30%
- **Profitable Pairs**: 2/8 (25.0%)


---

## Key Findings

### Correlation Insights

- **Crypto Intra**: Average correlation = 0.7240 (10 pairs)
- **Forex Intra**: Average correlation = -0.1015 (10 pairs)
- **Equity Intra**: Average correlation = 0.3853 (45 pairs)
- **Crypto Forex**: Average correlation = -0.0214 (25 pairs)

### Trading Strategy Insights

- Best performing strategy overall: **Momentum**
- Strong correlations (|r| ≥ 0.7) show potential for pairs trading strategies
- Mean reversion strategies work best on highly correlated pairs
- Momentum strategies benefit from trending markets


---

*Report generated on 2025-12-26 05:33:23*