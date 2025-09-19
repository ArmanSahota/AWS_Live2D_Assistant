import { useEffect, useRef, useState, useCallback } from 'react'

export interface Live2DModelInfo {
  url: string
  emotionMap?: Record<string, any>
  initialXshift?: number
  initialYshift?: number
  [key: string]: any
}

export interface UseLive2DOptions {
  onModelLoaded?: (model: any) => void
  onModelError?: (error: Error) => void
  autoResize?: boolean
}

export interface UseLive2DReturn {
  isLoaded: boolean
  isLoading: boolean
  error: string | null
  loadModel: (modelInfo: Live2DModelInfo) => Promise<void>
  clearModel: () => void
  playMotion: (motionName: string) => void
  setExpression: (expressionName: string) => void
}

export const useLive2D = (
  canvasRef: React.RefObject<HTMLCanvasElement>,
  options: UseLive2DOptions = {}
): UseLive2DReturn => {
  const {
    onModelLoaded,
    onModelError,
    autoResize = true
  } = options

  const [isLoaded, setIsLoaded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const appRef = useRef<any>(null)
  const modelRef = useRef<any>(null)
  const emoMapRef = useRef<Record<string, any> | null>(null)

  // Initialize PIXI Application
  const initializeApp = useCallback(() => {
    if (!canvasRef.current || appRef.current) return

    try {
      // Check if PIXI and Live2D are available
      if (typeof (window as any).PIXI === 'undefined') {
        throw new Error('PIXI.js not loaded. Make sure Live2D libraries are included.')
      }

      const PIXI = (window as any).PIXI
      
      appRef.current = new PIXI.Application({
        view: canvasRef.current,
        autoStart: true,
        resizeTo: canvasRef.current.parentElement,
        transparent: true,
        backgroundAlpha: 0,
      })

      console.log('[useLive2D] PIXI Application initialized')
      
      // Handle resize if enabled
      if (autoResize) {
        const resizeObserver = new ResizeObserver(() => {
          if (appRef.current && canvasRef.current) {
            appRef.current.renderer.resize(
              canvasRef.current.clientWidth,
              canvasRef.current.clientHeight
            )
          }
        })
        
        if (canvasRef.current.parentElement) {
          resizeObserver.observe(canvasRef.current.parentElement)
        }
        
        return () => resizeObserver.disconnect()
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize PIXI'
      console.error('[useLive2D] Initialization error:', errorMessage)
      setError(errorMessage)
      onModelError?.(error instanceof Error ? error : new Error(errorMessage))
    }
  }, [canvasRef, autoResize, onModelError])

  // Load Live2D model
  const loadModel = useCallback(async (modelInfo: Live2DModelInfo) => {
    if (!appRef.current) {
      console.error('[useLive2D] PIXI app not initialized')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const PIXI = (window as any).PIXI
      const live2d = PIXI.live2d

      if (!live2d) {
        throw new Error('Live2D plugin not loaded')
      }

      console.log('[useLive2D] Loading model:', modelInfo.url)
      emoMapRef.current = modelInfo.emotionMap || null

      // Clear existing model
      if (modelRef.current) {
        appRef.current.stage.removeChild(modelRef.current)
        modelRef.current.destroy({ children: true, texture: true, baseTexture: true })
        modelRef.current = null
      }

      // Resolve model URL
      let modelUrl = modelInfo.url
      if (!modelUrl.startsWith('http') && !modelUrl.startsWith('file:')) {
        // Use relative path for Vite/React
        modelUrl = modelUrl.replace(/^\/+/, '')
        // In React/Vite, static assets are served from the public directory
        if (!modelUrl.startsWith('/')) {
          modelUrl = '/' + modelUrl
        }
      }

      console.log('[useLive2D] Resolved model URL:', modelUrl)

      const options = {
        autoHitTest: false,
        autoFocus: false,
        autoUpdate: true,
      }

      const model = await live2d.Live2DModel.from(modelUrl, options)
      appRef.current.stage.addChild(model)

      // Scale and position model
      const vw = appRef.current.view.width
      const vh = appRef.current.view.height
      const naturalW = model.width || 1
      const naturalH = model.height || 1
      
      // Scale to fit with 10% margin
      const scale = Math.min(vw / naturalW, vh / naturalH) * 0.9
      model.scale.set(scale)
      
      // Set center anchor and position
      model.anchor.set(0.5, 0.5)
      model.position.set(vw / 2, vh / 2)

      // Apply initial position shifts
      if (modelInfo.initialXshift) {
        model.x += modelInfo.initialXshift
      }
      if (modelInfo.initialYshift) {
        model.y += modelInfo.initialYshift
      }

      // Make model draggable
      makeDraggable(model)
      setupMouseEvents(model)

      // Disable eye blink if needed
      if (model.internalModel) {
        model.internalModel.eyeBlink = null
      }

      modelRef.current = model
      
      // Expose model globally for backward compatibility
      ;(window as any).model2 = model

      setIsLoaded(true)
      setIsLoading(false)
      
      console.log('[useLive2D] Model loaded successfully')
      onModelLoaded?.(model)

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load model'
      console.error('[useLive2D] Model loading error:', errorMessage)
      setError(errorMessage)
      setIsLoading(false)
      onModelError?.(error instanceof Error ? error : new Error(errorMessage))
    }
  }, [onModelLoaded, onModelError])

  // Make model draggable
  const makeDraggable = useCallback((model: any) => {
    model.interactive = true
    model.buttonMode = true
    model.cursor = 'grab'
    
    const originalAlpha = model.alpha
    
    model.on('pointerdown', (e: any) => {
      if (e.data.button !== 0) return // Only left mouse button
      
      model.cursor = 'grabbing'
      model.alpha = 0.8
      model.dragging = true
      model._pointerX = e.data.global.x - model.x
      model._pointerY = e.data.global.y - model.y
      
      // Bring to front
      if (model.parent) {
        const index = model.parent.children.indexOf(model)
        if (index !== model.parent.children.length - 1) {
          model.parent.addChildAt(model, model.parent.children.length - 1)
        }
      }
      
      e.stopPropagation()
    })

    model.on('pointermove', (e: any) => {
      if (model.dragging) {
        model.position.x = e.data.global.x - model._pointerX
        model.position.y = e.data.global.y - model._pointerY
      }
    })

    const endDrag = () => {
      model.dragging = false
      model.cursor = 'grab'
      model.alpha = originalAlpha
    }

    model.on('pointerup', endDrag)
    model.on('pointerupoutside', endDrag)
  }, [])

  // Setup mouse events
  const setupMouseEvents = useCallback((model: any) => {
    // Mouse event setup will be expanded in future iterations
    console.log('[useLive2D] Mouse events set up for model')
  }, [])

  // Clear current model
  const clearModel = useCallback(() => {
    if (modelRef.current && appRef.current) {
      appRef.current.stage.removeChild(modelRef.current)
      modelRef.current.destroy({ children: true, texture: true, baseTexture: true })
      modelRef.current = null
      ;(window as any).model2 = null
    }
    setIsLoaded(false)
    setError(null)
  }, [])

  // Play motion
  const playMotion = useCallback((motionName: string) => {
    if (modelRef.current && modelRef.current.motion) {
      console.log('[useLive2D] Playing motion:', motionName)
      modelRef.current.motion(motionName)
    }
  }, [])

  // Set expression
  const setExpression = useCallback((expressionName: string) => {
    if (modelRef.current && emoMapRef.current && emoMapRef.current[expressionName]) {
      console.log('[useLive2D] Setting expression:', expressionName)
      const expressionIndex = emoMapRef.current[expressionName]
      if (modelRef.current.internalModel && modelRef.current.internalModel.coreModel) {
        modelRef.current.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', expressionIndex)
      }
    }
  }, [])

  // Initialize on mount
  useEffect(() => {
    const cleanup = initializeApp()
    
    return () => {
      // Cleanup
      clearModel()
      if (appRef.current) {
        appRef.current.destroy(true)
        appRef.current = null
      }
      if (cleanup) cleanup()
    }
  }, [initializeApp, clearModel])

  return {
    isLoaded,
    isLoading,
    error,
    loadModel,
    clearModel,
    playMotion,
    setExpression
  }
}