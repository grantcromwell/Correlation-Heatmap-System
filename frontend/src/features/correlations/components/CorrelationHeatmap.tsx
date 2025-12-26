import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../shared/api/client'
import { HeatmapResponse } from '../api/types'

interface CorrelationHeatmapProps {
  assetClasses: string[]
  timeframe?: string
  minCorrelation?: number
}

export default function CorrelationHeatmap({
  assetClasses,
  timeframe = '1m',
  minCorrelation = 0.5,
}: CorrelationHeatmapProps) {
  const { data, isLoading, error } = useQuery<HeatmapResponse>({
    queryKey: ['heatmap', assetClasses, timeframe, minCorrelation],
    queryFn: async () => {
      const response = await apiClient.get('/correlations/heatmap', {
        params: {
          asset_classes: assetClasses,
          timeframe,
          min_correlation: minCorrelation,
        },
      })
      return response.data
    },
  })

  if (isLoading) {
    return <div className="p-4">Loading heatmap data...</div>
  }

  if (error) {
    return <div className="p-4 text-red-600">Error loading heatmap data</div>
  }

  if (!data || data.heatmap_data.length === 0) {
    return <div className="p-4">No correlation data available</div>
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Correlation Heatmap</h2>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-sm text-gray-600 mb-4">
          Total pairs: {data.metadata.total_pairs} | Strong correlations: {data.metadata.strong_correlations}
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pair
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Correlation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P-Value
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.heatmap_data.map((pair, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pair.instrument_a} - {pair.instrument_b}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pair.correlation.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pair.p_value.toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

