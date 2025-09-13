/**
 * TTS Bridge Module
 * 
 * This module provides a bridge between the local TTS engine and the cloud TTS fallback.
 * It handles the TTS flow, error handling, and fallback logic.
 */

import { getFeatureFlags } from '../../config/appConfig';
import { ttsFallback } from '../../infra/http/api';
import { isLoggedIn } from '../../infra/auth/noneAuth';

// Define the TTS result interface
export interface TTSResult {
  success: boolean;
  audioData?: ArrayBuffer;
  error?: Error;
  source: 'local' | 'cloud';
  metrics?: {
    startTime: number;
    endTime: number;
    duration: number;
    textLength: number;
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

// Logger function
function log(level: LogLevel, message: string, data?: any): void {
  if (level >= currentLogLevel) {
    const prefix = LogLevel[level];
    if (data) {
      console[level >= LogLevel.WARN ? 'error' : 'log'](`[TTS:${prefix}] ${message}`, data);
    } else {
      console[level >= LogLevel.WARN ? 'error' : 'log'](`[TTS:${prefix}] ${message}`);
    }
  }
}

/**
 * Convert text to speech using the local TTS engine via IPC
 * @param text The text to convert to speech
 * @returns A promise that resolves to the TTS result
 */
async function localTTS(text: string): Promise<TTSResult> {
  const startTime = Date.now();
  log(LogLevel.INFO, `Generating TTS for text (${text.length} chars)`);
  
  try {
    // Call the local TTS engine via IPC
    // This is where we bridge from TypeScript to Python TTS engines
    const audioData = await window.api.generateSpeech(text);
    
    const endTime = Date.now();
    const metrics = {
      startTime,
      endTime,
      duration: endTime - startTime,
      textLength: text.length
    };
    
    log(LogLevel.INFO, `TTS generated successfully in ${metrics.duration}ms`);
    
    return {
      success: true,
      audioData,
      source: 'local',
      metrics
    };
  } catch (error) {
    const endTime = Date.now();
    log(LogLevel.ERROR, 'Local TTS failed:', error);
    
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
      source: 'local',
      metrics: {
        startTime,
        endTime,
        duration: endTime - startTime,
        textLength: text.length
      }
    };
  }
}

/**
 * Convert text to speech using the cloud TTS fallback
 * @param text The text to convert to speech
 * @param voice The voice to use
 * @returns A promise that resolves to the TTS result
 */
async function cloudTTS(text: string, voice: string = 'default'): Promise<TTSResult> {
  const startTime = Date.now();
  log(LogLevel.INFO, `Generating cloud TTS for text (${text.length} chars), voice: ${voice}`);
  
  try {
    if (!isLoggedIn()) {
      throw new Error('User is not authenticated for cloud TTS');
    }
    
    const audioData = await ttsFallback(text, voice);
    
    const endTime = Date.now();
    const metrics = {
      startTime,
      endTime,
      duration: endTime - startTime,
      textLength: text.length
    };
    
    log(LogLevel.INFO, `Cloud TTS generated successfully in ${metrics.duration}ms`);
    
    return {
      success: true,
      audioData,
      source: 'cloud',
      metrics
    };
  } catch (error) {
    const endTime = Date.now();
    log(LogLevel.ERROR, 'Cloud TTS failed:', error);
    
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
      source: 'cloud',
      metrics: {
        startTime,
        endTime,
        duration: endTime - startTime,
        textLength: text.length
      }
    };
  }
}

/**
 * Convert text to speech using the appropriate TTS engine
 * @param text The text to convert to speech
 * @param voice The voice to use for cloud TTS
 * @returns A promise that resolves to the TTS result
 */
export async function speak(text: string, voice: string = 'default'): Promise<TTSResult> {
  if (!text || text.trim().length === 0) {
    log(LogLevel.WARN, 'Attempted to speak empty text');
    return {
      success: false,
      error: new Error('Empty text provided'),
      source: 'local'
    };
  }
  
  const flags = getFeatureFlags();
  log(LogLevel.DEBUG, `Using TTS with flags:`, flags);
  
  // Check if local TTS is enabled
  if (flags.useLocalTTS) {
    const localResult = await localTTS(text);
    
    // If local TTS succeeded, return the result
    if (localResult.success) {
      return localResult;
    }
    
    // If local TTS failed and cloud fallbacks are enabled, try cloud TTS
    if (flags.useCloudFallbacks) {
      log(LogLevel.INFO, 'Local TTS failed, falling back to cloud TTS');
      return cloudTTS(text, voice);
    }
    
    // If cloud fallbacks are disabled, return the local error
    return localResult;
  }
  
  // If local TTS is disabled, use cloud TTS directly
  return cloudTTS(text, voice);
}

/**
 * Play audio data through the Live2D model or fallback to standard audio
 * @param audioData The audio data to play
 * @param expressionIndex Optional expression index for the Live2D model
 * @returns A promise that resolves when the audio has finished playing
 */
export function playAudio(
  audioData: ArrayBuffer, 
  expressionIndex?: number
): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      // Convert ArrayBuffer to base64
      const base64 = arrayBufferToBase64(audioData);
      
      // Call the audio system's addAudioTask function
      if (typeof window.addAudioTask === 'function') {
        window.addAudioTask(
          base64,         // audio_base64
          "None",         // instrument_base64
          [],             // volumes
          0,              // slice_length
          null,           // text
          expressionIndex !== undefined ? [expressionIndex] : null // expression_list
        );
        resolve();
      } else {
        // Fallback to basic audio playback if addAudioTask is not available
        log(LogLevel.WARN, 'window.addAudioTask not available, using basic audio playback');
        const blob = new Blob([audioData], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        
        audio.onended = () => {
          URL.revokeObjectURL(url);
          resolve();
        };
        
        audio.onerror = (error) => {
          URL.revokeObjectURL(url);
          reject(error);
        };
        
        audio.play().catch(error => {
          URL.revokeObjectURL(url);
          reject(error);
        });
      }
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Convert ArrayBuffer to base64 string
 * @param buffer The ArrayBuffer to convert
 * @returns The base64 string
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  
  return window.btoa(binary);
}

/**
 * Check if TTS is available
 * @returns True if TTS is available, false otherwise
 */
export async function isTTSAvailable(): Promise<boolean> {
  try {
    const flags = getFeatureFlags();
    
    // Check if local TTS is enabled and available
    if (flags.useLocalTTS) {
      // Check if window.api.generateSpeech is available
      if (typeof window.api?.generateSpeech !== 'function') {
        log(LogLevel.WARN, 'Local TTS API is not available');
        return false;
      }
      
      return true;
    }
    
    // Check if cloud TTS is available
    if (flags.useCloudFallbacks) {
      if (!isLoggedIn()) {
        log(LogLevel.WARN, 'Not logged in for cloud TTS');
        return false;
      }
      
      return true;
    }
    
    return false;
  } catch (error) {
    log(LogLevel.ERROR, 'Error checking TTS availability:', error);
    return false;
  }
}

// Initialize event listeners for window.api once the window is loaded
window.addEventListener('DOMContentLoaded', () => {
  // Check if TTS is available and log the result
  isTTSAvailable().then(available => {
    log(LogLevel.INFO, `TTS availability check: ${available ? 'AVAILABLE' : 'NOT AVAILABLE'}`);
  });
});
