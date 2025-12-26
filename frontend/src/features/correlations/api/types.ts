export interface CorrelationPair {
  instrument_a: string
  instrument_b: string
  correlation: number
  p_value: number
  h3_index: string
  asset_class_a: string
  asset_class_b: string
  last_updated: string
}

export interface HeatmapMetadata {
  total_pairs: number
  strong_correlations: number
  generated_at: string
}

export interface HeatmapResponse {
  heatmap_data: CorrelationPair[]
  metadata: HeatmapMetadata
}

export interface DiscoveredCorrelation {
  id: string
  instrument_pair: [string, string]
  correlation: number
  discovered_at: string
  h3_index: string
  backtest_results: any
  spanning_tree_data: any
  status: string
}

export interface DiscoveredCorrelationsResponse {
  discoveries: DiscoveredCorrelation[]
  pagination: {
    page: number
    per_page: number
    total: number
  }
}

