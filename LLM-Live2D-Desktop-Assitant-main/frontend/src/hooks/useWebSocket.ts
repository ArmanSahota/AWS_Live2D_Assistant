import { useEffect, useRef, useState, useCallback } from 'react'
import { API_CONFIG, WS_MESSAGE_TYPES, getWebSocketURL } from '../config/api'

export interface WebSocketMessage {
  type: string
  text?: string
  message?: string
  [key: string]: any
}

export interface UseWebSocketOptions {
  autoConnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export interface UseWebSocketReturn {
  isConnected: boolean
  isConnecting: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: WebSocketMessage) => void
  connect: () => void
  disconnect: () => void
  reconnect: () => void
  connectionAttempts: number
}

export const useWebSocket = (
  endpoint: string = '/client-ws',
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionAttempts, setConnectionAttempts] = useState(0)

  const ws = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null)
  const isReconnecting = useRef(false)

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      console.log('[useWebSocket] Already connected')
      return
    }

    if (isConnecting) {
      console.log('[useWebSocket] Connection already in progress')
      return
    }

    setIsConnecting(true)
    
    try {
      const wsUrl = getWebSocketURL(endpoint)
      console.log(`[useWebSocket] Connecting to: ${wsUrl}`)
      
      ws.current = new WebSocket(wsUrl)
      
      ws.current.onopen = () => {
        console.log('[useWebSocket] Connected successfully')
        setIsConnected(true)
        setIsConnecting(false)
        setConnectionAttempts(0)
        isReconnecting.current = false
        
        // Clear any existing reconnect timer
        if (reconnectTimer.current) {
          clearTimeout(reconnectTimer.current)
          reconnectTimer.current = null
        }
        
        onConnect?.()
      }
      
      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('[useWebSocket] Message received:', message.type)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('[useWebSocket] Failed to parse message:', error)
        }
      }
      
      ws.current.onclose = (event) => {
        console.log(`[useWebSocket] Connection closed: ${event.code} - ${event.reason}`)
        setIsConnected(false)
        setIsConnecting(false)
        
        onDisconnect?.()
        
        // Auto-reconnect if not manually disconnected and within attempt limits
        if (!isReconnecting.current && connectionAttempts < maxReconnectAttempts) {
          console.log(`[useWebSocket] Scheduling reconnect attempt ${connectionAttempts + 1}/${maxReconnectAttempts}`)
          isReconnecting.current = true
          
          reconnectTimer.current = setTimeout(() => {
            setConnectionAttempts(prev => prev + 1)
            connect()
          }, reconnectInterval)
        } else if (connectionAttempts >= maxReconnectAttempts) {
          console.error('[useWebSocket] Max reconnection attempts reached')
        }
      }
      
      ws.current.onerror = (error) => {
        console.error('[useWebSocket] WebSocket error:', error)
        setIsConnecting(false)
        onError?.(error)
      }
      
    } catch (error) {
      console.error('[useWebSocket] Failed to create WebSocket:', error)
      setIsConnecting(false)
    }
  }, [endpoint, connectionAttempts, maxReconnectAttempts, reconnectInterval, onConnect, onDisconnect, onError, onMessage, isConnecting])

  const disconnect = useCallback(() => {
    console.log('[useWebSocket] Manually disconnecting')
    isReconnecting.current = false
    
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current)
      reconnectTimer.current = null
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect')
      ws.current = null
    }
    
    setIsConnected(false)
    setIsConnecting(false)
    setConnectionAttempts(0)
  }, [])

  const reconnect = useCallback(() => {
    console.log('[useWebSocket] Manual reconnect requested')
    disconnect()
    setTimeout(() => connect(), 100)
  }, [connect, disconnect])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        const messageString = JSON.stringify(message)
        ws.current.send(messageString)
        console.log('[useWebSocket] Message sent:', message.type)
      } catch (error) {
        console.error('[useWebSocket] Failed to send message:', error)
      }
    } else {
      console.warn('[useWebSocket] Cannot send message - WebSocket not connected')
    }
  }, [])

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect()
    }
    
    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    reconnect,
    connectionAttempts
  }
}