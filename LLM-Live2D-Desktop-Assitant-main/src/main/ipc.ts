/**
 * IPC Module
 * 
 * This module handles IPC communication between the main process and renderer process.
 * It registers handlers for various IPC events.
 */

import { ipcMain, BrowserWindow } from 'electron';
import { askClaude } from './claudeClient';
import { readConfig, saveConfig, getFeatureFlags, updateFeatureFlags, getAWSConfig, updateAWSConfig } from '../config/appConfig';
import { HealthResponse } from '../types/http';
import { spawn } from 'child_process';
import { join } from 'path';
import * as fs from 'fs';
import * as os from 'os';

// Cache for speech-related items
const speechCache = {
  currentSpeechProcess: null as any,
  lastTranscription: '',
  speechStatus: 'idle'
};

/**
 * Initialize IPC handlers
 */
export function initializeIPC(): void {
  // Claude API handlers
  ipcMain.handle('claude:ask', async (_event, text: string) => {
    return askClaude(text);
  });

  // Health check handler
  ipcMain.handle('health:get', async () => {
    const config = readConfig();
    const httpBase = config.httpBase;
    
    if (!httpBase) {
      throw new Error('HTTP base URL is not configured');
    }
    
    const startTime = Date.now();
    const response = await fetch(`${httpBase}/health`);
    const latency = Date.now() - startTime;
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json() as HealthResponse;
    return { ...data, latency };
  });

  // Configuration handlers
  ipcMain.handle('config:get', async () => {
    return readConfig();
  });

  ipcMain.handle('config:set', async (_event, partial) => {
    saveConfig(partial);
    return readConfig();
  });
  
  // Feature flag handlers
  ipcMain.handle('get-feature-flags', async () => {
    return getFeatureFlags();
  });
  
  ipcMain.handle('update-feature-flags', async (_event, flags) => {
    updateFeatureFlags(flags);
    return getFeatureFlags();
  });
  
  // AWS config handlers
  ipcMain.handle('get-aws-config', async () => {
    return getAWSConfig();
  });
  
  ipcMain.handle('update-aws-config', async (_event, config) => {
    updateAWSConfig(config);
    return getAWSConfig();
  });
  
  // Speech generation handler
  ipcMain.handle('speech:generate', async (_event, text: string) => {
    return generateSpeech(text);
  });
  
  // Speech stop handler
  ipcMain.on('speech:stop', (_event) => {
    if (speechCache.currentSpeechProcess) {
      try {
        speechCache.currentSpeechProcess.kill();
        speechCache.currentSpeechProcess = null;
      } catch (error) {
        console.error('Error stopping speech process:', error);
      }
    }
  });
  
  // Microphone device handlers
  ipcMain.handle('get-microphone-devices', async () => {
    // In a real implementation, this would use a node module to get the microphone devices
    // For now, we'll return a mock list
    return [
      { id: 'default', name: 'Default Microphone' },
      { id: 'mic1', name: 'Microphone 1' },
      { id: 'mic2', name: 'Microphone 2' }
    ];
  });
  
  ipcMain.on('set-microphone-device', (_event, deviceId) => {
    console.log(`Setting microphone device to ${deviceId}`);
    // In a real implementation, this would set the microphone device
  });
}

/**
 * Generate speech from text using the appropriate TTS engine
 * @param text The text to convert to speech
 * @returns A promise that resolves to the audio data as an ArrayBuffer
 */
async function generateSpeech(text: string): Promise<ArrayBuffer> {
  // Update speech status
  speechCache.speechStatus = 'generating';
  notifySpeechStatus('generating');
  
  try {
    // Generate a temporary file path for the audio
    const tempDir = os.tmpdir();
    const tempFile = join(tempDir, `speech-${Date.now()}.wav`);
    
    // Call the Python TTS script
    const pythonScript = join(process.cwd(), 'tts', 'generate_speech.py');
    
    // Create a promise that resolves when the process completes
    return new Promise<ArrayBuffer>((resolve, reject) => {
      try {
        // In a real implementation, this would call the actual TTS engine
        // For now, we'll simulate a delay and return a dummy WAV file
        
        // Simulating a process
        setTimeout(() => {
          // Create a simple WAV file (this is just a placeholder - not a real WAV)
          const buffer = Buffer.alloc(1024);
          fs.writeFileSync(tempFile, buffer);
          
          // Read the file and return as ArrayBuffer
          const audioData = fs.readFileSync(tempFile);
          const arrayBuffer = audioData.buffer.slice(
            audioData.byteOffset,
            audioData.byteOffset + audioData.byteLength
          );
          
          // Clean up the temporary file
          fs.unlinkSync(tempFile);
          
          // Update speech status
          speechCache.speechStatus = 'idle';
          notifySpeechStatus('idle');
          
          resolve(arrayBuffer);
        }, 500);
      } catch (error) {
        // Update speech status
        speechCache.speechStatus = 'error';
        notifySpeechStatus('error');
        
        console.error('Error generating speech:', error);
        reject(error);
      }
    });
  } catch (error) {
    // Update speech status
    speechCache.speechStatus = 'error';
    notifySpeechStatus('error');
    
    console.error('Error in generateSpeech:', error);
    throw error;
  }
}

/**
 * Notify the renderer process about speech status changes
 * @param status The current speech status
 */
function notifySpeechStatus(status: string): void {
  const windows = BrowserWindow.getAllWindows();
  for (const window of windows) {
    window.webContents.send('speech:status', status);
  }
}
