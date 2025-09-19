/**
 * IPC Module
 * 
 * This module handles IPC communication between the main process and renderer process.
 * It registers handlers for various IPC events.
 */

const { ipcMain, BrowserWindow } = require('electron');
const { askClaude } = require('./claudeClient');
const { readConfig, saveConfig, getFeatureFlags, updateFeatureFlags, getAWSConfig, updateAWSConfig } = require('../config/appConfig');
const { spawn } = require('child_process');
const { join } = require('path');
const fs = require('fs');
const os = require('os');
const { listModels, findDefaultModel, resolveModelsRoot } = require('./models');

// Guard to prevent double registration of IPC handlers
let ipcRegistered = false;

// Cache for speech-related items
const speechCache = {
  currentSpeechProcess: null,
  lastTranscription: '',
  speechStatus: 'idle',
  transcriptionHistory: []
};

/**
 * Helper function to safely register IPC handlers
 * Removes any existing handler before adding a new one
 */
function handleOnce(channel, handler) {
  try { 
    ipcMain.removeHandler(channel); 
    console.log(`Removed existing handler for channel: ${channel}`);
  } catch (error) {
    // Handler didn't exist, which is fine
  }
  ipcMain.handle(channel, handler);
  console.log(`Registered handler for channel: ${channel}`);
}

/**
 * Safe handle function for use in other modules
 * This is a more concise alias for handleOnce
 */
const handle = handleOnce;

/**
 * Safe handle function for use in other modules
 */
const safeHandle = handleOnce;

/**
 * Initialize IPC handlers
 */
function initializeIPC() {
  // Prevent double registration
  if (ipcRegistered) {
    console.log('IPC handlers already registered, skipping initialization');
    return;
  }
  ipcRegistered = true;
  console.log('Initializing IPC handlers...');
  
  // Claude API handlers
  handleOnce('claude:ask', async (_event, text) => {
    console.log(`Claude request: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
    const result = await askClaude(text);
    console.log(`Claude response received: ${result.substring(0, 50)}${result.length > 50 ? '...' : ''}`);
    return result;
  });

  // Health check handler
  handleOnce('health:get', async () => {
    const config = readConfig();
    const httpBase = config.httpBase;
    
    console.log(`Health check using HTTP base: ${httpBase}`);
    
    if (!httpBase) {
      throw new Error('HTTP base URL is not configured');
    }
    
    const startTime = Date.now();
    const response = await fetch(`${httpBase}/health`);
    const latency = Date.now() - startTime;
    
    if (!response.ok) {
      console.error(`Health check failed: ${response.status} ${response.statusText}`);
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Health check successful: ${JSON.stringify(data)}, latency: ${latency}ms`);
    return { ...data, latency };
  });

  // Configuration handlers
  handleOnce('config:get', async () => {
    const config = readConfig();
    console.log(`Config retrieved: httpBase=${config.httpBase}`);
    return config;
  });

  handleOnce('config:set', async (_event, partial) => {
    console.log(`Updating config: ${JSON.stringify(partial)}`);
    saveConfig(partial);
    return readConfig();
  });
  
  // Feature flag handlers
  handleOnce('get-feature-flags', async () => {
    const flags = getFeatureFlags();
    console.log(`Feature flags retrieved: ${JSON.stringify(flags)}`);
    return flags;
  });
  
  handleOnce('update-feature-flags', async (_event, flags) => {
    console.log(`Updating feature flags: ${JSON.stringify(flags)}`);
    updateFeatureFlags(flags);
    return getFeatureFlags();
  });
  
  // AWS config handlers
  handleOnce('get-aws-config', async () => {
    const awsConfig = getAWSConfig();
    console.log(`AWS config retrieved: region=${awsConfig.region}`);
    return awsConfig;
  });
  
  handleOnce('update-aws-config', async (_event, config) => {
    console.log(`Updating AWS config: ${JSON.stringify(config)}`);
    updateAWSConfig(config);
    return getAWSConfig();
  });
  
  // Speech generation handler
  handleOnce('speech:generate', async (_event, text) => {
    console.log(`Generating speech for text: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
    const result = await generateSpeech(text);
    console.log(`Speech generation complete, audio size: ${result.byteLength} bytes`);
    return result;
  });
  
  // Speech stop handler
  ipcMain.on('speech:stop', (_event) => {
    console.log('Stopping speech process');
    if (speechCache.currentSpeechProcess) {
      try {
        speechCache.currentSpeechProcess.kill();
        speechCache.currentSpeechProcess = null;
        console.log('Speech process stopped successfully');
      } catch (error) {
        console.error('Error stopping speech process:', error);
      }
    }
  });
  
  // Microphone device handlers
  handleOnce('get-microphone-devices', async () => {
    console.log('Getting microphone devices');
    // This will be updated to use the devices sent from the renderer
    return speechCache.microphoneDevices || [];
  });
  
  ipcMain.on('set-microphone-device', (_event, deviceId) => {
    console.log(`Setting microphone device to ${deviceId}`);
    // In a real implementation, this would set the microphone device
  });
  
  // Handle microphone devices from renderer
  ipcMain.on('set-microphone-devices', (_event, devices) => {
    console.log(`Received microphone devices from renderer: ${devices.length} devices`);
    // Store the devices for later retrieval
    speechCache.microphoneDevices = devices;
  });
  
  // Handle transcription logging
  ipcMain.on('log:transcription', (_event, text) => {
    // Store the transcription in history
    speechCache.lastTranscription = text;
    speechCache.transcriptionHistory.push({
      timestamp: new Date().toISOString(),
      text
    });
    
    // Keep only the last 50 transcriptions
    if (speechCache.transcriptionHistory.length > 50) {
      speechCache.transcriptionHistory.shift();
    }
    
    // Log to console
    console.log(`[STT Transcription] "${text}"`);
    
    // Notify all windows about the transcription
    const windows = BrowserWindow.getAllWindows();
    for (const window of windows) {
      window.webContents.send('speech:transcription', text);
    }
  });
  
  // Authentication IPC handlers
  handleOnce('is-logged-in', async () => {
    const isLoggedIn = global.authToken !== null;
    console.log(`Auth status check: ${isLoggedIn ? 'logged in' : 'not logged in'}`);
    return isLoggedIn;
  });
  
  handleOnce('login', async () => {
    try {
      const config = getAWSConfig();
      const authUrl = `${config.cognitoDomain}/login?client_id=${config.cognitoClientId}&response_type=token&scope=email+openid+profile&redirect_uri=myapp://auth`;
      
      console.log(`Opening auth URL: ${authUrl}`);
      
      // Open the auth URL in the default browser
      const { shell } = require('electron');
      await shell.openExternal(authUrl);
      return true;
    } catch (error) {
      console.error('Error during login:', error);
      return false;
    }
  });
  
  handleOnce('logout', async () => {
    console.log('Logging out user');
    if (global.setAuthToken) {
      global.setAuthToken(null);
    }
    return true;
  });
  
  // Live2D model handlers
  handle('models:list', async () => {
    console.log('Listing available Live2D models');
    return listModels();
  });
  
  handle('models:default', async () => {
    console.log('Getting default Live2D model');
    return findDefaultModel();
  });
  
  handle('models:root', async () => {
    console.log('Getting Live2D models root directory');
    return resolveModelsRoot();
  });
  
  handle('models:resolve-path', async (_event, model) => {
    console.log(`Resolving model3 path for model: ${model.name}`);
    return resolveModel3Path(model);
  });
}

/**
 * Resolves the model3.json path for a given model
 * @param {Object} model - The model object with name, dir, conf, and model3 properties
 * @returns {string|null} The resolved path to the model3.json file or null if not found
 */
function resolveModel3Path(model) {
  try {
    // If model already has a model3 path, return it
    if (model.model3 && fs.existsSync(model.model3)) {
      return model.model3;
    }
    
    // If model has a conf file, try to parse it for model3 path
    if (model.conf && fs.existsSync(model.conf)) {
      try {
        const confContent = fs.readFileSync(model.conf, 'utf8');
        // Simple YAML parsing for model3 field
        const model3Match = confContent.match(/model3:\s*(.+)/);
        if (model3Match) {
          const model3RelativePath = model3Match[1].trim().replace(/['"]/g, '');
          const model3FullPath = path.resolve(model.dir, model3RelativePath);
          if (fs.existsSync(model3FullPath)) {
            return model3FullPath;
          }
        }
      } catch (confError) {
        console.warn(`Failed to parse conf file for model ${model.name}:`, confError);
      }
    }
    
    // Fallback: scan directory for *.model3.json files
    if (model.dir && fs.existsSync(model.dir)) {
      const files = fs.readdirSync(model.dir);
      const model3File = files.find(f => f.toLowerCase().endsWith('.model3.json'));
      if (model3File) {
        return path.join(model.dir, model3File);
      }
    }
    
    console.warn(`Could not resolve model3 path for model: ${model.name}`);
    return null;
  } catch (error) {
    console.error(`Error resolving model3 path for model ${model.name}:`, error);
    return null;
  }
}

/**
 * Get the transcription history
 * @returns The transcription history
 */
function getTranscriptionHistory() {
  return speechCache.transcriptionHistory;
}

/**
 * Generate speech from text using the appropriate TTS engine
 * @param text The text to convert to speech
 * @returns A promise that resolves to the audio data as an ArrayBuffer
 */
async function generateSpeech(text) {
  // Update speech status
  speechCache.speechStatus = 'generating';
  notifySpeechStatus('generating');
  
  console.log(`[TTS] Generating speech for: "${text}"`);
  
  try {
    // Generate a temporary file path for the audio
    const tempDir = os.tmpdir();
    const tempFile = join(tempDir, `speech-${Date.now()}.wav`);
    
    return new Promise((resolve, reject) => {
      try {
        // Create a Python process to generate speech using pyttsx3TTS
        // ENHANCED FIX: Improved Windows path handling and error handling
        const tempFileFixed = tempFile.replace(/\\/g, '/');
        const cwdFixed = process.cwd().replace(/\\/g, '/');
        
        // SECURITY FIX: Use JSON encoding to prevent Python code injection
        const textJson = JSON.stringify(text);
        const tempFileJson = JSON.stringify(tempFileFixed);
        
        // Enhanced Python script with better error handling and secure text handling
        const pythonScript = `
import sys
import os
import json
import traceback
import asyncio
try:
    sys.path.append('${cwdFixed}')
    from tts.tts_factory import TTSFactory
    
    # Use EDGE_TTS engine to match configuration
    engine = TTSFactory.get_tts_engine("EDGE_TTS",
        voice="en-US-JennyNeural",
        rate="+0%",
        pitch="+0Hz",
        volume="+0%")
    
    # Use JSON to safely decode the text and file path
    text_to_speak = json.loads(${textJson})
    output_file = json.loads(${tempFileJson})
    
    # Generate audio with EDGE_TTS (synchronous call)
    result = engine.synthesize(text_to_speak)
    if isinstance(result, tuple):
        file_path, duration = result
    else:
        file_path = result
    
    print(f"SUCCESS:{file_path}")
except ImportError as e:
    print(f"IMPORT_ERROR:Failed to import TTS modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"TTS_ERROR:{e}")
    traceback.print_exc()
    sys.exit(2)
        `;
        
        const pythonProcess = spawn('python', ['-c', pythonScript]);
        
        speechCache.currentSpeechProcess = pythonProcess;
        
        let outputData = '';
        pythonProcess.stdout.on('data', (data) => {
          outputData += data.toString();
        });
        
        pythonProcess.stderr.on('data', (data) => {
          console.error(`TTS Error: ${data}`);
        });
        
        pythonProcess.on('close', (code) => {
          // ENHANCED ERROR HANDLING: Parse structured output from Python script
          const output = outputData.trim();
          
          if (code !== 0 || output.startsWith('IMPORT_ERROR:') || output.startsWith('TTS_ERROR:')) {
            let errorMessage = `TTS process failed with code ${code}`;
            
            if (output.startsWith('IMPORT_ERROR:')) {
              errorMessage = `TTS Import Error: ${output.substring(13)}`;
            } else if (output.startsWith('TTS_ERROR:')) {
              errorMessage = `TTS Generation Error: ${output.substring(10)}`;
            }
            
            console.error(errorMessage);
            speechCache.speechStatus = 'error';
            notifySpeechStatus('error');
            reject(new Error(errorMessage));
            return;
          }
          
          // Extract the file path from the enhanced output format
          let filePath;
          if (output.startsWith('SUCCESS:')) {
            filePath = output.substring(8).trim();
          } else {
            // Fallback: try to extract from legacy format
            const match = output.match(/Finished Generating (.*\.aiff)/);
            filePath = match ? match[1].trim() : output;
          }
          
          console.log(`TTS generated file at: ${filePath}`);
          
          // Read the audio file
          try {
            const audioData = fs.readFileSync(filePath);
            const arrayBuffer = audioData.buffer.slice(
              audioData.byteOffset,
              audioData.byteOffset + audioData.byteLength
            );
            
            // Clean up the temporary file
            try {
              fs.unlinkSync(filePath);
              console.log(`Temporary audio file deleted: ${filePath}`);
            } catch (unlinkError) {
              console.warn(`Could not delete temporary file: ${unlinkError.message}`);
            }
            
            // Update speech status
            speechCache.speechStatus = 'idle';
            notifySpeechStatus('idle');
            
            resolve(arrayBuffer);
          } catch (error) {
            console.error('Error reading audio file:', error);
            console.error('File path attempted:', filePath);
            console.error('Raw output from TTS process:', outputData);
            speechCache.speechStatus = 'error';
            notifySpeechStatus('error');
            reject(error);
          }
        });
      } catch (error) {
        speechCache.speechStatus = 'error';
        notifySpeechStatus('error');
        console.error('Error generating speech:', error);
        reject(error);
      }
    });
  } catch (error) {
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
function notifySpeechStatus(status) {
  const windows = BrowserWindow.getAllWindows();
  for (const window of windows) {
    window.webContents.send('speech:status', status);
  }
}

module.exports = { initializeIPC, getTranscriptionHistory, safeHandle: handle };
