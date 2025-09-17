// Load environment variables from .env file
require('dotenv').config();

const { app, BrowserWindow, Menu, Tray, ipcMain, screen, nativeImage, shell, desktopCapturer } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const Store = require('electron-store');

// Import configuration module
const { readConfig, updateConfig, getFeatureFlags, updateFeatureFlags, getAWSConfig, updateAWSConfig } = require('./src/config/appConfig');

// Import IPC module
const { initializeIPC, getTranscriptionHistory } = require('./src/main/ipc.js');

// Authentication state
let authToken = null;

const isDevelopment = !app.isPackaged;
let basePath;
if (isDevelopment) {
  basePath = __dirname;
} else {
  basePath = path.join(process.resourcesPath, 'app.asar.unpacked');
}
console.log('Base path is:', basePath);

let mainWindow;
let tray = null;
let contextMenu;
let currentConfigFile = '';
let configFiles = [];
let backendProcess = null; // FIX: Added missing declaration
const isMac = process.platform === 'darwin';


async function updateContextMenu() {
  const configMenuItems = configFiles.map(configFile => {
    return {
      label: configFile,
      type: 'radio',
      checked: configFile === currentConfigFile,
      click: () => switchConfig(configFile)
    };
  });

  // Simple config menu items

  contextMenu = Menu.buildFromTemplate([
    { label: 'Show Subtitles', type: 'checkbox', checked: true, click: (menuItem) => toggleSubtitles(menuItem.checked) },
    { label: 'Microphone', type: 'checkbox', checked: true, click: (menuItem) => toggleMicrophone(menuItem.checked) },
    { 
      label: 'Select Microphone',
      click: () => showMicrophoneSelectionDialog()
    },
    { label: 'Allow Interruption', type: 'checkbox', checked: false, click: (menuItem) => toggleInterruption(menuItem.checked) },
    { label: 'Wake-up', type: 'checkbox', checked: false, click: (menuItem) => toggleWakeUp(menuItem.checked) },
    { label: 'Hide', type: 'checkbox', checked: false, click: (menuItem) => toggleMinimize(menuItem.checked) },
    {
      label: 'Speech Sensitivity',
      submenu: [
        { label: 'Very High (70%)', type: 'radio', checked: false, click: () => setSensitivity(0.7) },
        { label: 'High (80%)', type: 'radio', checked: false, click: () => setSensitivity(0.8) },
        { label: 'Medium (90%)', type: 'radio', checked: true, click: () => setSensitivity(0.9) },
        { label: 'Low (95%)', type: 'radio', checked: false, click: () => setSensitivity(0.95) },
        { label: 'Very Low (99%)', type: 'radio', checked: false, click: () => setSensitivity(0.99) }
      ]
    },
    {
      label: 'Switch Config',
      submenu: configMenuItems
    },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  if (tray) {
    tray.setContextMenu(contextMenu);
  }
}

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    x: 0,
    y: 0,
    transparent: true,
    frame: false,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false,
    focusable: true,
    acceptFirstMouse: true,
    backgroundColor: '#00000000',
    fullscreen: false,
    kiosk: false,
    webPreferences: {
      preload: path.join(basePath, 'static', 'desktop', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: true,
      enableRemoteModule: true,
      sandbox: false,
    },
  });

  mainWindow.loadFile(path.join(basePath, 'static', 'desktop.html'));
  // mainWindow.webContents.openDevTools();

  if (isMac) mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // Allow mouse events initially so the user can interact with the window
  mainWindow.setIgnoreMouseEvents(false);
  mainWindow.setAlwaysOnTop(true, 'screen-saver');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });

  createTray();
}

function createTray() {
  let iconPath = path.join(basePath, 'static', 'pictures', 'icon.png');
  let trayIcon;

  if (isMac) {
    trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 });
    tray = new Tray(trayIcon);
  } else {
    tray = new Tray(iconPath);
  }
  tray.setToolTip('Elaina');

  if (!contextMenu) {
    updateContextMenu();
  } else {
    tray.setContextMenu(contextMenu);
  }
}


function toggleSubtitles(isChecked) {
  mainWindow.webContents.send('toggle-subtitles', isChecked);
}

function toggleMicrophone(isChecked) {
  mainWindow.webContents.send('toggle-microphone', isChecked);
}

function toggleInterruption(isChecked) {
  mainWindow.webContents.send('toggle-interruption', isChecked);
}

function toggleWakeUp(isChecked) {
  mainWindow.webContents.send('toggle-wake-up', isChecked);
}

function toggleMinimize(isChecked) {
  if (isChecked) {
    mainWindow.minimize();
  } else {
    mainWindow.restore();
    mainWindow.setAlwaysOnTop(true, 'screen-saver');
  }
}

function switchConfig(configFile) {
  currentConfigFile = configFile;
  mainWindow.webContents.send('switch-config', configFile);
}

function setSensitivity(value) {
  mainWindow.webContents.send('set-sensitivity', value);
}

// Use whenReady() to ensure initializeIPC() is only called once
app.whenReady().then(() => {
  console.log('Electron app is ready');
  
  // Initialize IPC handlers - this should only happen once
  console.log('Initializing IPC handlers...');
  initializeIPC();
  
  if (isDevelopment) {
    console.log('Starting backend in development mode...');
    startBackend();
    console.log('Waiting for backend to start before creating window...');
    setTimeout(() => {
      createWindow();
    }, 3000);
  }
  else {
    console.log('Creating window in production mode...');
    createWindow();
  }
});

app.on('window-all-closed', function () {
  if (!isMac) {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('will-quit', () => {
  if (isDevelopment) stopBackend();
});



function startBackend() {
  const pythonExecutable = "python"

  const scriptPath = path.join(basePath, 'server.py');
  console.log(`Starting backend with script: ${scriptPath}`);

  backendProcess = spawn(pythonExecutable, [scriptPath], {
    cwd: basePath,
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });

  backendProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`[Backend] ${output.trim()}`);
  });

  backendProcess.stderr.on('data', (data) => {
    const output = data.toString();
    console.error(`[Backend Error] ${output.trim()}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    if (code !== 0 && !app.isQuitting) {
      console.log('Attempting to restart backend...');
      setTimeout(() => {
        startBackend();
      }, 5000);
    }
  });
  
  console.log('Backend process started');
}


function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend process...');
    backendProcess.kill();
    backendProcess = null;
    console.log('Backend process stopped');
  }
}

ipcMain.on('set-ignore-mouse-events', (event, ignore) => {
  if (isMac) mainWindow.setIgnoreMouseEvents(ignore);
  else mainWindow.setIgnoreMouseEvents(ignore, { forward: true });
});

ipcMain.on('show-context-menu', (event, x, y) => {
  // Make sure contextMenu is initialized before trying to use it
  if (!contextMenu) {
    updateContextMenu().then(() => {
      contextMenu.popup({
        window: mainWindow,
        x: x,
        y: y,
      });
    });
  } else {
    contextMenu.popup({
      window: mainWindow,
      x: x,
      y: y,
    });
  }
});

ipcMain.on('update-menu-checked', (event, label, checked) => {
  const menuItem = contextMenu.items.find(item => item.label === label);
  if (menuItem) {
    menuItem.checked = checked;
    Menu.setApplicationMenu(Menu.buildFromTemplate(contextMenu.items));
    tray.setContextMenu(contextMenu);
  }
});

ipcMain.on('update-config-files', (event, files) => {
  configFiles = files;
  updateContextMenu();
});

ipcMain.on('update-sensitivity', (event, value) => {
  const sensitivityMenu = contextMenu.items.find(item => item.label === 'Speech Sensitivity');
  if (sensitivityMenu) {
    const threshold = value * 100;
    sensitivityMenu.submenu.items.forEach(item => {
      item.checked = item.label.includes(`(${threshold}%)`);
    });
  }
});

ipcMain.handle('get-clipboard-content', async () => {
    const content = {};
    const { clipboard } = require('electron');
    
    try {
        content.text = clipboard.readText() || '';
        
        const image = clipboard.readImage();
        if (!image.isEmpty()) {
            const scaledImage = image.resize({
                width: 800,
                height: 800,
                quality: 'good'
            });
            content.image = scaledImage.toPNG().toString('base64');
        } else {
            content.image = null;
        }
    } catch (error) {
        console.error('Error getting clipboard content:', error);
        content.text = '';
        content.image = null;
    }
    
    return content;
});

// Get transcription history
ipcMain.handle('get-transcription-history', async () => {
    return getTranscriptionHistory();
});

// Log transcription
ipcMain.on('log:transcription', (_event, text) => {
    console.log(`[STT Transcription] "${text}"`);
});

// Add test functions
ipcMain.handle('test:claude', async () => {
    console.log('Running Claude API test...');
    try {
        const { askClaude } = require('./src/main/claudeClient');
        const response = await askClaude('Say hello in a friendly way.');
        console.log(`Claude test response: ${response}`);
        return { success: true, response };
    } catch (error) {
        console.error('Claude test failed:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('test:tts', async () => {
    console.log('Running TTS test...');
    try {
        const { generateSpeech } = require('./src/main/ipc');
        const text = 'This is a test of the text to speech system.';
        const audioData = await generateSpeech(text);
        console.log(`TTS test generated ${audioData.byteLength} bytes of audio`);
        return { success: true, size: audioData.byteLength };
    } catch (error) {
        console.error('TTS test failed:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('test:pipeline', async () => {
    console.log('Running full pipeline test...');
    try {
        const { askClaude } = require('./src/main/claudeClient');
        const { generateSpeech } = require('./src/main/ipc');
        
        // Step 1: Call Claude
        console.log('Step 1: Calling Claude API...');
        const text = 'Tell me a short joke.';
        const response = await askClaude(text);
        console.log(`Claude response: ${response}`);
        
        // Step 2: Generate speech
        console.log('Step 2: Generating speech...');
        const audioData = await generateSpeech(response);
        console.log(`Generated ${audioData.byteLength} bytes of audio`);
        
        return { 
            success: true, 
            claudeResponse: response,
            audioSize: audioData.byteLength
        };
    } catch (error) {
        console.error('Pipeline test failed:', error);
        return { success: false, error: error.message };
    }
});

// Configuration IPC handlers are now handled in src/main/ipc.js

// Microphone selection
async function showMicrophoneSelectionDialog() {
  // Use the devices sent from the renderer
  const store = new Store();
  const microphoneDevices = store.get('microphoneDevices') || [];
  
  const microphoneMenu = Menu.buildFromTemplate(
    microphoneDevices.map(device => ({
      label: device.name,
      click: () => {
        mainWindow.webContents.send('select-microphone', device.id);
      }
    }))
  );
  
  microphoneMenu.popup({ window: mainWindow });
}

// Handle microphone device requests is now handled in src/main/ipc.js

// Handle microphone devices from renderer
ipcMain.on('set-microphone-devices', (_event, devices) => {
  // Store the devices for later retrieval
  const store = new Store();
  store.set('microphoneDevices', devices);
  
  // Update the microphone selection dialog
  if (mainWindow) {
    mainWindow.webContents.send('microphone-devices-updated', devices);
  }
});

// set-microphone-device is now handled in src/main/ipc.js

// Authentication state management
function setAuthToken(token) {
  authToken = token;
  
  // Notify renderer process
  if (mainWindow) {
    mainWindow.webContents.send('auth-callback', { success: true, token: authToken });
  }
}

// Export auth token for IPC module
global.authToken = authToken;
global.setAuthToken = setAuthToken;

// Register custom URL protocol handler for auth callback
if (isDevelopment) {
  app.setAsDefaultProtocolClient('myapp');
} else {
  // In production, use the packaged app path
  app.setAsDefaultProtocolClient('myapp', process.execPath);
}

// Handle custom URL protocol
app.on('open-url', (event, url) => {
  event.preventDefault();
  
  if (url.startsWith('myapp://auth')) {
    // Extract token from URL
    const urlObj = new URL(url);
    const hashParams = new URLSearchParams(urlObj.hash.substring(1));
    authToken = hashParams.get('id_token');
    
    // Notify renderer process
    if (mainWindow) {
      mainWindow.webContents.send('auth-callback', { success: true, token: authToken });
    }
  }
});
