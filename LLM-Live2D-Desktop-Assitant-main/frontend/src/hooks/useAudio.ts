import { useState, useCallback, useRef } from 'react'

export interface AudioTask {
  id: string
  audio_base64: string
  instrument_base64?: string
  volumes?: any
  slice_length?: number
  text?: string
  expression_list?: any
}

export interface UseAudioOptions {
  chunkSize?: number
  onAudioStart?: (task: AudioTask) => void
  onAudioEnd?: (task: AudioTask) => void
  onAudioError?: (error: Error, task: AudioTask) => void
}

export interface UseAudioReturn {
  isPlaying: boolean
  currentTask: AudioTask | null
  queueLength: number
  addAudioTask: (
    audio_base64: string,
    instrument_base64?: string,
    volumes?: any,
    slice_length?: number,
    text?: string,
    expression_list?: any
  ) => void
  clearQueue: () => void
  stopCurrent: () => void
  isRecording: boolean
  startRecording: () => Promise<void>
  stopRecording: () => Promise<Blob | null>
}

export const useAudio = (options: UseAudioOptions = {}): UseAudioReturn => {
  const {
    chunkSize = 4096,
    onAudioStart,
    onAudioEnd,
    onAudioError
  } = options

  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTask, setCurrentTask] = useState<AudioTask | null>(null)
  const [queueLength, setQueueLength] = useState(0)
  const [isRecording, setIsRecording] = useState(false)

  const audioQueue = useRef<AudioTask[]>([])
  const currentAudio = useRef<HTMLAudioElement | null>(null)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const recordedChunks = useRef<Blob[]>([])

  // Process audio queue
  const processQueue = useCallback(async () => {
    if (isPlaying || audioQueue.current.length === 0) return

    const task = audioQueue.current.shift()
    if (!task) return

    setCurrentTask(task)
    setIsPlaying(true)
    setQueueLength(audioQueue.current.length)

    try {
      console.log('[useAudio] Playing audio task:', task.id, task.text)
      onAudioStart?.(task)

      // Update subtitle if text is provided
      if (task.text) {
        const messageElement = document.getElementById('message')
        if (messageElement) {
          messageElement.textContent = task.text
          console.log('[useAudio] Subtitle updated:', task.text)
        }
      }

      // Play audio
      await playAudioBase64(task.audio_base64)

      console.log('[useAudio] Audio task completed:', task.id)
      onAudioEnd?.(task)

    } catch (error) {
      console.error('[useAudio] Audio task failed:', error)
      onAudioError?.(error instanceof Error ? error : new Error('Audio playback failed'), task)
    } finally {
      setIsPlaying(false)
      setCurrentTask(null)
      
      // Process next task in queue
      setTimeout(processQueue, 100)
    }
  }, [isPlaying, onAudioStart, onAudioEnd, onAudioError])

  // Play base64 audio
  const playAudioBase64 = useCallback((audio_base64: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const audio = new Audio(`data:audio/wav;base64,${audio_base64}`)
        currentAudio.current = audio

        audio.onended = () => {
          console.log('[useAudio] Audio playback ended')
          currentAudio.current = null
          resolve()
        }

        audio.onerror = (error) => {
          console.error('[useAudio] Audio playback error:', error)
          currentAudio.current = null
          reject(new Error('Audio playback failed'))
        }

        audio.play().catch(reject)
      } catch (error) {
        reject(error)
      }
    })
  }, [])

  // Add audio task to queue
  const addAudioTask = useCallback((
    audio_base64: string,
    instrument_base64?: string,
    volumes?: any,
    slice_length?: number,
    text?: string,
    expression_list?: any
  ) => {
    const task: AudioTask = {
      id: `audio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      audio_base64,
      instrument_base64,
      volumes,
      slice_length,
      text,
      expression_list
    }

    console.log('[useAudio] Adding audio task to queue:', task.id, text)
    audioQueue.current.push(task)
    setQueueLength(audioQueue.current.length)

    // Start processing if not already playing
    if (!isPlaying) {
      processQueue()
    }
  }, [isPlaying, processQueue])

  // Clear audio queue
  const clearQueue = useCallback(() => {
    console.log('[useAudio] Clearing audio queue')
    audioQueue.current = []
    setQueueLength(0)
  }, [])

  // Stop current audio
  const stopCurrent = useCallback(() => {
    if (currentAudio.current) {
      console.log('[useAudio] Stopping current audio')
      currentAudio.current.pause()
      currentAudio.current.currentTime = 0
      currentAudio.current = null
    }
    setIsPlaying(false)
    setCurrentTask(null)
  }, [])

  // Start audio recording
  const startRecording = useCallback(async (): Promise<void> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      })

      recordedChunks.current = []
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.current.push(event.data)
        }
      }

      mediaRecorder.current.start(100) // Collect data every 100ms
      setIsRecording(true)
      console.log('[useAudio] Recording started')

    } catch (error) {
      console.error('[useAudio] Failed to start recording:', error)
      throw error
    }
  }, [])

  // Stop audio recording
  const stopRecording = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorder.current || !isRecording) {
        resolve(null)
        return
      }

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(recordedChunks.current, { type: 'audio/webm' })
        console.log('[useAudio] Recording stopped, blob size:', blob.size)
        
        // Stop all tracks
        if (mediaRecorder.current?.stream) {
          mediaRecorder.current.stream.getTracks().forEach(track => track.stop())
        }
        
        setIsRecording(false)
        resolve(blob)
      }

      mediaRecorder.current.stop()
    })
  }, [isRecording])

  // Expose functions globally for backward compatibility
  useCallback(() => {
    const windowAny = window as any
    windowAny.addAudioTask = addAudioTask
    windowAny.clearAudioQueue = clearQueue
    windowAny.stopCurrentAudio = stopCurrent
    windowAny.startAudioRecording = startRecording
    windowAny.stopAudioRecording = stopRecording
    
    // Initialize audio task queue if not exists
    if (!windowAny.audioTaskQueue) {
      windowAny.audioTaskQueue = {
        addTask: (taskFn: () => Promise<void>) => {
          // Simple queue implementation
          taskFn().catch(console.error)
        }
      }
    }
  }, [addAudioTask, clearQueue, stopCurrent, startRecording, stopRecording])

  return {
    isPlaying,
    currentTask,
    queueLength,
    addAudioTask,
    clearQueue,
    stopCurrent,
    isRecording,
    startRecording,
    stopRecording
  }
}