// Simple test script to verify Live2D model loading

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// Import the models module
const { resolveModelsRoot, listModels, findDefaultModel } = require('./src/main/models');

/**
 * Resolves a model3 path for a model
 * @param {Object} model The model object
 * @returns {string} The resolved path to the model3 file
 */
function resolveModel3Path(model) {
  console.log("DEBUG: Resolving model3 path for:", model);
  
  // If model3 is already defined, return it
  if (model.model3) {
    console.log("DEBUG: Model3 path already defined:", model.model3);
    return model.model3;
  }

  // Otherwise, try to extract from conf.yml
  if (model.conf) {
    try {
      const yaml = require('js-yaml');
      const confContent = fs.readFileSync(model.conf, 'utf8');
      const confData = yaml.load(confContent);
      
      console.log("DEBUG: Loaded conf.yml:", confData);
      
      if (confData && confData.model3) {
        // Resolve relative to the model directory
        const model3Path = path.join(model.dir, confData.model3);
        console.log("DEBUG: Resolved model3 path from conf:", model3Path);
        return model3Path;
      }
    } catch (error) {
      console.error("Error loading conf.yml:", error);
    }
  }
  
  console.log("DEBUG: Failed to resolve model3 path");
  return null;
}

// Initialize the IPC handlers for models
function initializeModelIPC() {
  ipcMain.handle('models:list', async () => {
    console.log("IPC: Listing available Live2D models");
    const models = listModels();
    console.log("Found models:", models);
    return models;
  });
  
  ipcMain.handle('models:default', async () => {
    console.log("IPC: Getting default Live2D model");
    const model = findDefaultModel();
    console.log("Default model:", model);
    return model;
  });
  
  ipcMain.handle('models:root', async () => {
    console.log("IPC: Getting Live2D models root directory");
    const root = resolveModelsRoot();
    console.log("Models root:", root);
    return root;
  });
  
  ipcMain.handle('models:resolve-path', async (event, model) => {
    console.log("IPC: Resolving model3 path for:", model);
    const resolvedPath = resolveModel3Path(model);
    console.log("Resolved path:", resolvedPath);
    return resolvedPath;
  });

  // Add minimal config handler
  ipcMain.handle('config:get', async () => {
    console.log("IPC: Getting config");
    return { live2d: null }; // Return null to force fallback to models API
  });

  // Add feature flags handler
  ipcMain.handle('get-feature-flags', async () => {
    console.log("IPC: Getting feature flags");
    return {};
  });

  // Add dummy handlers for other IPC channels to avoid errors
  ipcMain.handle('claude:ask', async () => "This is a dummy response");
  ipcMain.handle('speech:generate', async () => Buffer.from("dummy audio"));
  ipcMain.handle('health:get', async () => ({ status: "OK" }));
  ipcMain.handle('get-microphone-devices', async () => []);
  ipcMain.handle('get-transcription-history', async () => []);

  console.log("All IPC handlers initialized");
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'static', 'desktop', 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Load the desktop HTML file
  mainWindow.loadFile(path.join(__dirname, 'static', 'desktop.html'));
  
  // Open the DevTools to inspect console output
  mainWindow.webContents.openDevTools();

  console.log("Window created, loading desktop.html");
}

app.whenReady().then(() => {
  console.log("App ready");
  initializeModelIPC();
  console.log("Creating window");
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

console.log("Test script initialized");