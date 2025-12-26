import { useEffect, useState } from 'react'
import WebSocketClient from '../../../shared/api/websocket/client'

export function useWebSocketUpdates() {
  const [updates, setUpdates] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const wsClient = new WebSocketClient()

    wsClient.connect(
      (data) => {
        setUpdates((prev) => [...prev, data])
      },
      (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
    )

    setIsConnected(true)

    return () => {
      wsClient.disconnect()
    }
  }, [])

  return { updates, isConnected }
}

