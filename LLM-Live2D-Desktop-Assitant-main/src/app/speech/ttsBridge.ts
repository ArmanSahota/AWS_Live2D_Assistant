/**
 * TTS Bridge Module
 * 
 * This module provides a bridge between the local TTS engine and the cloud TTS fallback.
 * It handles the TTS flow, error handling, and fallback logic.
 */

import { getFeatureFlags } from '../../config/appConfig';
import { ttsFallback } from '../../infra/http/api';
import { isLoggedIn } from '../../infra/auth/cognitoAuth';

// Define the TTS result interface
export interface TTSResult {
  success: boolean;
  audioData?: ArrayBuffer;
  error?: Error;
  source: 'local' | 'cloud';
}

/**
 * Convert text to speech using the local TTS engine
 * @param text The text to convert to speech
 * @returns A promise that resolves to the TTS result
 */
async function localTTS(text: string): Promise<TTSResult> {
  try {
    // This is a placeholder for the actual local TTS implementation
    // In a real implementation, this would call the existing local TTS engine
    
    // For now, we'll simulate a successful local TTS call
    // In the actual implementation, this would return the audio data from the local TTS engine
    
    // Simulate a delay for the TTS processing
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Return a successful result
    return {
      success: true,
      audioData: new ArrayBuffer(0), // This would be the actual audio data
      source: 'local'
    };
  } catch (error) {
    console.error('Local TTS failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
      source: 'local'
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
  try {
    if (!isLoggedIn()) {
      throw new Error('User is not authenticated');
    }
    
    const audioData = await ttsFallback(text, voice);
    
    return {
      success: true,
      audioData,
      source: 'cloud'
    };
  } catch (error) {
    console.error('Cloud TTS failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
      source: 'cloud'
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
  const flags = getFeatureFlags();
  
  // Check if local TTS is enabled
  if (flags.useLocalTTS) {
    const localResult = await localTTS(text);
    
    // If local TTS succeeded, return the result
    if (localResult.success) {
      return localResult;
    }
    
    // If local TTS failed and cloud fallbacks are enabled, try cloud TTS
    if (flags.useCloudFallbacks) {
      console.log('Local TTS failed, falling back to cloud TTS');
      return cloudTTS(text, voice);
    }
    
    // If cloud fallbacks are disabled, return the local error
    return localResult;
  }
  
  // If local TTS is disabled, use cloud TTS directly
  return cloudTTS(text, voice);
}

/**
 * Play audio data
 * @param audioData The audio data to play
 * @returns A promise that resolves when the audio has finished playing
 */
export function playAudio(audioData: ArrayBuffer): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      // Create an audio context
      const audioContext = new AudioContext();
      
      // Decode the audio data
      audioContext.decodeAudioData(audioData, (buffer) => {
        // Create a source node
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        
        // Connect the source to the destination (speakers)
        source.connect(audioContext.destination);
        
        // Play the audio
        source.start(0);
        
        // Resolve the promise when the audio has finished playing
        source.onended = () => {
          resolve();
        };
      }, (error) => {
        reject(error);
      });
    } catch (error) {
      reject(error);
    }
  });
}
