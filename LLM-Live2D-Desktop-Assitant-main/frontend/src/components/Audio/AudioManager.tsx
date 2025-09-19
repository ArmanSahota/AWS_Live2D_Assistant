import React, { useEffect } from 'react'
import { useAudio } from '../../hooks/useAudio'

export const AudioManager: React.FC = () => {
  const {
    isPlaying,
    currentTask,
    queueLength,
    addAudioTask,
    clearQueue,
    stopCurrent,
    isRecording,
    startRecording,
    stopRecording
  } = useAudio({
    onAudioStart: (task) => {
      console.log('[AudioManager] Audio started:', task.text)
      // Update global state for backward compatibility
      ;(window as any).state = 'playing'
    },
    onAudioEnd: (task) => {
      console.log('[AudioManager] Audio ended:', task.text)
      // Update global state for backward compatibility
      ;(window as any).state = 'idle'
    },
    onAudioError: (error, task) => {
      console.error('[AudioManager] Audio error:', error, task)
      ;(window as any).state = 'error'
    }
  })

  // Initialize global state and functions for backward compatibility
  useEffect(() => {
    const windowAny = window as any
    
    // Initialize global state
    if (!windowAny.state) {
      windowAny.state = 'idle'
    }
    if (!windowAny.fullResponse) {
      windowAny.fullResponse = ''
    }
    
    // Expose audio functions globally
    windowAny.addAudioTask = addAudioTask
    windowAny.clearAudioQueue = clearQueue
    windowAny.stopCurrentAudio = stopCurrent
    windowAny.startMicrophone = startRecording
    windowAny.stopMicrophone = stopRecording
    
    // Audio task queue for backward compatibility
    if (!windowAny.audioTaskQueue) {
      windowAny.audioTaskQueue = {
        addTask: (taskFn: () => Promise<void>) => {
          taskFn().catch(console.error)
        }
      }
    }

    return () => {
      // Cleanup global references
      delete windowAny.addAudioTask
      delete windowAny.clearAudioQueue
      delete windowAny.stopCurrentAudio
      delete windowAny.startMicrophone
      delete windowAny.stopMicrophone
    }
  }, [addAudioTask, clearQueue, stopCurrent, startRecording, stopRecording])

  // Handle interruption state - Update window.state for backward compatibility
  useEffect(() => {
    const windowAny = window as any
    
    if (isPlaying) {
      windowAny.state = 'playing'
    } else if (isRecording) {
      windowAny.state = 'recording'
    } else {
      windowAny.state = 'idle'
    }
    
    console.log('[AudioManager] Global state updated:', windowAny.state)
  }, [isPlaying, isRecording])

  return (
    <div style={{ display: 'none' }}>
      {/* Audio Manager - Manages audio playback and recording */}
      {/* Status: {isPlaying ? 'Playing' : isRecording ? 'Recording' : 'Idle'} */}
      {/* Queue: {queueLength} tasks */}
      {/* Current: {currentTask?.text || 'None'} */}
    </div>
  )
}