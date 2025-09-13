/**
 * STT Bridge Module
 * 
 * This module provides a bridge between the local STT engine and the app.
 * It handles the STT flow, error handling, and status reporting.
 */

import { getFeatureFlags } from '../../config/appConfig';

// Define the STT result interface
export interface STTResult {
  success: boolean;
  text?: string;
  error?: Error;
  source: 'local' | 'cloud';
  metrics?: {
    startTime: number;
    endTime: number;
    duration: number;
    confidence?: number;
  };
}

// Define logging levels
enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

// Current log level - can be adjusted via config
const currentLogLevel = LogLevel.INFO;

// Status of speech recognition
export enum SpeechStatus {
  IDLE = 'idle',
  LISTENING = 'listening',
  PROCESSING = 'processing',
  ERROR = 'error'
}

// Status callbacks
type StatusCallback = (status: SpeechStatus) => void;
const statusCallbacks: StatusCallback[] = [];

// Current status
let currentStatus = SpeechStatus.IDLE;

// Logger function
function log(level: LogLevel, message: string, data?: any): void {
  if (level >= currentLogLevel) {
    const prefix = LogLevel[level];
    if (data) {
      console[level >= LogLevel.WARN ? 'error' : 'log'](`[STT:${prefix}] ${message}`, data);
    } else {
      console[level >= LogLevel.WARN ? 'error' : 'log'](`[STT:${prefix}] ${message}`);
    }
  }
}

/**
 * Update the STT status and notify listeners
 * @param status The new status
 */
function updateStatus(status: SpeechStatus): void {
  if (currentStatus !== status) {
    log(LogLevel.INFO, `STT status changed from ${currentStatus} to ${status}`);
    currentStatus = status;
    statusCallbacks.forEach(callback => callback(status));
  }
}

/**
 * Register a status callback
 * @param callback The callback function
 */
export function onStatus(callback: StatusCallback): void {
  statusCallbacks.push(callback);
  // Call immediately with current status
  callback(currentStatus);
}

/**
 * Transcribe speech using the local STT engine
 * @returns A promise that resolves to the STT result
 */
export async function transcribe(audioBuffer?: ArrayBuffer): Promise<STTResult> {
  const startTime = Date.now();
  updateStatus(SpeechStatus.LISTENING);
  
  try {
    // If audioBuffer is provided, use it directly
    // Otherwise, listen for speech using the microphone
    if (!audioBuffer || audioBuffer.byteLength === 0) {
      log(LogLevel.INFO, 'Starting speech recognition using microphone');
      
      if (typeof window.start_mic !== 'function') {
        throw new Error('Microphone access function is not available');
      }
      
      updateStatus(SpeechStatus.LISTENING);
      
      // Use the VAD/STT system via window functions
      try {
        // This should trigger the microphone to listen
        // The result will come through a callback or event we need to listen for
        await window.start_mic();
        
        // Wait for the VAD to detect speech and then silence
        // This is a temporary implementation that needs to be replaced with proper event handling
        return new Promise<STTResult>((resolve) => {
          // In a real implementation, we would listen for a specific event
          // For now, we'll use a timeout as a placeholder
          const timeout = setTimeout(() => {
            updateStatus(SpeechStatus.IDLE);
            window.stop_mic?.();
            resolve({
              success: false,
              error: new Error('Speech recognition timed out'),
              source: 'local'
            });
          }, 30000); // 30-second timeout
          
          // In a real implementation, we would set up an event listener here
          // that would clear the timeout and resolve the promise when speech is detected
          
          // Placeholder for the actual event handling
          // This should be replaced with actual event listeners
          // window.addEventListener('speechrecognitionresult', (event) => {
          //   clearTimeout(timeout);
          //   updateStatus(SpeechStatus.IDLE);
          //   window.stop_mic?.();
          //   resolve({
          //     success: true,
          //     text: event.detail.text,
          //     source: 'local',
          //     metrics: {
          //       startTime,
          //       endTime: Date.now(),
          //       duration: Date.now() - startTime,
          //       confidence: event.detail.confidence
          //     }
          //   });
          // });
        });
      } catch (error) {
        updateStatus(SpeechStatus.ERROR);
        log(LogLevel.ERROR, 'Error starting speech recognition:', error);
        return {
          success: false,
          error: error instanceof Error ? error : new Error(String(error)),
          source: 'local'
        };
      }
    } else {
      // Process provided audio buffer
      log(LogLevel.INFO, `Processing provided audio buffer (${audioBuffer.byteLength} bytes)`);
      updateStatus(SpeechStatus.PROCESSING);
      
      // In a real implementation, this would send the audio buffer to the STT engine
      // For now, we'll simulate a successful transcription
      await new Promise(resolve => setTimeout(resolve, 500));
      
      updateStatus(SpeechStatus.IDLE);
      return {
        success: true,
        text: "This is a placeholder transcription for testing purposes.",
        source: 'local',
        metrics: {
          startTime,
          endTime: Date.now(),
          duration: Date.now() - startTime
        }
      };
    }
  } catch (error) {
    updateStatus(SpeechStatus.ERROR);
    log(LogLevel.ERROR, 'STT transcription failed:', error);
    
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
      source: 'local',
      metrics: {
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime
      }
    };
  }
}

/**
 * Listen for speech once and return the transcription
 * @returns A promise that resolves to the STT result
 */
export async function listenOnce(): Promise<STTResult> {
  log(LogLevel.INFO, 'Starting single speech recognition session');
  return transcribe();
}

/**
 * Check if STT is available
 * @returns True if STT is available, false otherwise
 */
export async function isSTTAvailable(): Promise<boolean> {
  try {
    const flags = getFeatureFlags();
    
    // Check if local STT is enabled and available
    if (flags.useLocalTTS) {
      // Check if window functions are available
      if (typeof window.start_mic !== 'function' || typeof window.stop_mic !== 'function') {
        log(LogLevel.WARN, 'Local STT functions are not available');
        return false;
      }
      
      return true;
    }
    
    return false;
  } catch (error) {
    log(LogLevel.ERROR, 'Error checking STT availability:', error);
    return false;
  }
}

// Initialize event listeners for window.api once the window is loaded
window.addEventListener('DOMContentLoaded', () => {
  // Check if STT is available and log the result
  isSTTAvailable().then(available => {
    log(LogLevel.INFO, `STT availability check: ${available ? 'AVAILABLE' : 'NOT AVAILABLE'}`);
  });
  
  // Set up event listeners for speech detection
  // This is a placeholder for proper event handling
  // In a real implementation, we would use actual custom events
});
