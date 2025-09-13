# Live2D Desktop Assistant Fixes

This document outlines the fixes implemented to address issues with the Live2D Desktop Assistant application.

## 1. Live2D Model Loading Fixes

### Problem
The Live2D model was not loading correctly due to:
- Reliance on conf.yml files that might not exist
- Incorrect path resolution in development vs. production environments
- No fallback mechanism for missing configuration
- Pink screen or zoomed-in model issues

### Solution
- Created a robust model loading system that works with or without conf.yml files
- Added fallback to *.model3.json files when conf.yml is missing
- Implemented proper path resolution for both development and production environments
- Fixed styling issues to prevent pink screen and improve model scaling
- Decoupled Live2D initialization from WebSocket events

### Implementation Details
- Added `src/main/models.ts` to handle model discovery and loading
- Updated IPC handlers to expose model-related functions to the renderer
- Modified preload script to expose model API to the renderer
- Updated Live2D loader to use the new model API
- Added CSS styling to fix rendering issues

## 2. Port Allocation Fixes

### Problem
- Backend server was failing to find available ports
- No proper cleanup of used ports

### Solution
- Updated server.py to use a wider range of ports (1025-1050)
- Implemented proper cleanup of used ports
- Added better error handling for port allocation failures

## 3. Speech Pipeline Fixes

### Problem
- Speech-to-text (STT) transcription not being sent to Claude
- Text-to-speech (TTS) generation failing with edge-tts
- Live2D model not responding to speech input

### Solution
- Modified `src/main/ipc.js` to use pyttsx3TTS instead of edge-tts
- Updated the STT configuration to use whisper_cpp_asr
- Added proper logging of transcription results to terminal
- Implemented path tracing for data flow

## 4. Diagnostic Features

### Problem
- Difficult to diagnose issues in the pipeline
- No visual indicators for component status

### Solution
- Added visual indicators for pipeline status
- Created test functions for each component
- Implemented comprehensive logging throughout the application
- Added toast notifications for important events

### Implementation Details
- Created `static/desktop/diagnostics.js` for status indicators and notifications
- Added CSS styling for status indicators
- Updated WebSocket handler to report connection status
- Added event listeners for component status changes

## 5. Packaging Improvements

### Problem
- Model files not properly included in packaged application
- Path resolution issues in packaged application

### Solution
- Updated electron-builder configuration to properly include model files
- Added asarUnpack rules for model files
- Implemented proper path resolution for packaged application

### Implementation Details
- Updated package.json with proper electron-builder configuration
- Added extraResources configuration to copy model files to resources folder
- Created validation script to check model files before packaging

## 6. Additional Improvements

- Added model validation script (`scripts/validate-models.js`)
- Created template conf.yml for model folders
- Added CSS styling for better UI appearance
- Improved error handling throughout the application
- Added documentation for model configuration

## Usage

### Running the Application
```bash
npm start
```

### Validating Models
```bash
npm run validate-models
```

### Building the Application
```bash
npm run build
```

## Model Configuration

Models can be configured in two ways:

1. Using a conf.yml file in the model folder:
```yaml
name: ModelName
model3: model/ModelName.model3.json
scale: 0.15
offsetX: 0
offsetY: 0
```

2. Using the model3.json file directly (no conf.yml needed)

The application will automatically find and load available models.
