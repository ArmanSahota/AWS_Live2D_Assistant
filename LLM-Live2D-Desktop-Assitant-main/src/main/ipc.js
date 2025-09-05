/**
 * IPC Module
 * 
 * This module handles IPC communication between the main process and renderer process.
 * It registers handlers for various IPC events.
 */

const { ipcMain } = require('electron');
const { askClaude } = require('./claudeClient');
const { readConfig, saveConfig } = require('../config/appConfig');

/**
 * Initialize IPC handlers
 */
function initializeIPC() {
  // Claude API handlers
  ipcMain.handle('claude:ask', async (_event, text) => {
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
    
    const data = await response.json();
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
}

module.exports = { initializeIPC };
