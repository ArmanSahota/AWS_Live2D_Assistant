import React, { useEffect, useRef } from 'react'
import { useLive2D, Live2DModelInfo } from '../../hooks/useLive2D'

export const Live2DViewer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  
  const {
    isLoaded,
    isLoading,
    error,
    loadModel,
    clearModel,
    playMotion,
    setExpression
  } = useLive2D(canvasRef, {
    onModelLoaded: (model) => {
      console.log('[Live2DViewer] Model loaded successfully:', model)
      // Expose functions globally for backward compatibility
      const windowAny = window as any
      windowAny.playLive2DMotion = playMotion
      windowAny.setLive2DExpression = setExpression
      windowAny.clearLive2DModel = clearModel
    },
    onModelError: (error) => {
      console.error('[Live2DViewer] Model loading error:', error)
    },
    autoResize: true
  })

  // Listen for model loading messages from WebSocket
  useEffect(() => {
    const handleSetModel = (event: CustomEvent) => {
      const modelInfo: Live2DModelInfo = event.detail
      console.log('[Live2DViewer] Received model info:', modelInfo)
      loadModel(modelInfo)
    }

    // Listen for custom events from WebSocket component
    window.addEventListener('live2d-set-model', handleSetModel as EventListener)
    
    return () => {
      window.removeEventListener('live2d-set-model', handleSetModel as EventListener)
    }
  }, [loadModel])

  // Load default model on mount
  useEffect(() => {
    // Load default model after a short delay to ensure libraries are loaded
    const timer = setTimeout(() => {
      const defaultModelInfo: Live2DModelInfo = {
        url: '/desktop/models/default/default.model3.json',
        emotionMap: {},
        initialXshift: 0,
        initialYshift: 0
      }
      
      console.log('[Live2DViewer] Loading default model')
      loadModel(defaultModelInfo)
    }, 1000)

    return () => clearTimeout(timer)
  }, [loadModel])

  // Render loading state or error
  const renderOverlay = () => {
    if (error) {
      return (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'white',
          textAlign: 'center',
          backgroundColor: 'rgba(255, 0, 0, 0.8)',
          padding: '20px',
          borderRadius: '8px',
          zIndex: 10
        }}>
          <h3>Live2D Error</h3>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              backgroundColor: 'white',
              color: 'red',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }

    if (isLoading) {
      return (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'white',
          textAlign: 'center',
          zIndex: 10
        }}>
          <h3>Loading Live2D Model...</h3>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid rgba(255, 255, 255, 0.3)',
            borderTop: '4px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '10px auto'
          }}></div>
        </div>
      )
    }

    if (!isLoaded) {
      return (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'white',
          textAlign: 'center',
          zIndex: 10
        }}>
          <h3>Live2D Viewer</h3>
          <p>Initializing...</p>
        </div>
      )
    }

    return null
  }

  return (
    <div id="live2d-stage" style={{ position: 'relative', width: '100%', height: '100%' }}>
      <canvas 
        ref={canvasRef}
        id="live2d-canvas"
        style={{ 
          width: '100%', 
          height: '100%',
          display: 'block'
        }}
      />
      {renderOverlay()}
      
      {/* Add CSS for loading animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}