import React, { useEffect } from 'react'
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket'
import { WS_MESSAGE_TYPES } from '../../config/api'

export const WebSocketClient: React.FC = () => {
  const {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    reconnect,
    connectionAttempts
  } = useWebSocket('/client-ws', {
    autoConnect: true,
    onMessage: handleWebSocketMessage,
    onConnect: () => console.log('[WebSocketClient] Connected to main WebSocket'),
    onDisconnect: () => console.log('[WebSocketClient] Disconnected from main WebSocket'),
    onError: (error) => console.error('[WebSocketClient] WebSocket error:', error)
  })

  function handleWebSocketMessage(message: WebSocketMessage) {
    console.log('[WebSocketClient] Received message:', message.type, message)
    
    switch (message.type) {
      case WS_MESSAGE_TYPES.FULL_TEXT:
        // Update UI message
        const messageElement = document.getElementById('message')
        if (messageElement && message.text) {
          messageElement.textContent = message.text
        }
        break
        
      case WS_MESSAGE_TYPES.SET_MODEL:
        console.log('[WebSocketClient] Model set:', message.text)
        // Live2D model setting will be handled by Live2D component
        break
        
      case WS_MESSAGE_TYPES.CONTROL:
        console.log('[WebSocketClient] Control message:', message.text)
        // Control messages (start-mic, etc.)
        break
        
      case WS_MESSAGE_TYPES.CONFIG_SWITCHED:
        console.log('[WebSocketClient] Config switched:', message.message)
        break
        
      case WS_MESSAGE_TYPES.ERROR:
        console.error('[WebSocketClient] Server error:', message.message)
        break
        
      default:
        console.log('[WebSocketClient] Unhandled message type:', message.type)
    }
  }

  // Send initial connection messages
  useEffect(() => {
    if (isConnected) {
      // Request initial configuration
      sendMessage({
        type: WS_MESSAGE_TYPES.FETCH_CONFIGS
      })
    }
  }, [isConnected, sendMessage])

  // Expose WebSocket functions globally for backward compatibility
  useEffect(() => {
    // Make WebSocket functions available globally for existing code
    const windowAny = window as any
    windowAny.sendWebSocketMessage = sendMessage
    windowAny.reconnectWebSocket = reconnect
    windowAny.isWebSocketConnected = () => isConnected
    
    return () => {
      // Cleanup global references
      delete windowAny.sendWebSocketMessage
      delete windowAny.reconnectWebSocket
      delete windowAny.isWebSocketConnected
    }
  }, [sendMessage, reconnect, isConnected])

  return (
    <div style={{ display: 'none' }}>
      {/* WebSocket Client - Connection managed via hook */}
      {/* Connection status: {isConnected ? 'Connected' : isConnecting ? 'Connecting' : 'Disconnected'} */}
      {/* Attempts: {connectionAttempts} */}
    </div>
  )
}