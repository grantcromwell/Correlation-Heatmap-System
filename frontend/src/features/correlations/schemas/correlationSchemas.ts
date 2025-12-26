import { z } from 'zod'

export const heatmapQuerySchema = z.object({
  asset_classes: z.array(z.string()).min(1),
  timeframe: z.string().default('1m'),
  min_correlation: z.number().min(-1).max(1).default(0.5),
  lookback_days: z.number().min(30).max(2520).default(252),
})

export const backtestRequestSchema = z.object({
  instrument_pair: z.array(z.string()).length(2),
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  strategy: z.enum(['pairs_trading', 'momentum', 'mean_reversion']),
})

export type HeatmapQuery = z.infer<typeof heatmapQuerySchema>
export type BacktestRequest = z.infer<typeof backtestRequestSchema>

