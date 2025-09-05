const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // Existing APIs
    onToggleSubtitles: (callback) => ipcRenderer.on('toggle-subtitles', (event, data) => callback(data)),
    onToggleMicrophone: (callback) => ipcRenderer.on('toggle-microphone', (event, data) => callback(data)),
    onToggleInterruption: (callback) => ipcRenderer.on('toggle-interruption', (event, data) => callback(data)),
    onToggleWakeUp: (callback) => ipcRenderer.on('toggle-wake-up', (event, data) => callback(data)),
    onSelectMicrophone: (callback) => ipcRenderer.on('select-microphone', (event, deviceId) => callback(deviceId)),
    getMicrophoneDevices: () => ipcRenderer.invoke('get-microphone-devices'),
    setMicrophoneDevice: (deviceId) => ipcRenderer.send('set-microphone-device', deviceId),
    sendConfigFiles: (files) => ipcRenderer.send('update-config-files', files),
    onSwitchConfig: (callback) => ipcRenderer.on('switch-config', (event, data) => callback(data)),
    setIgnoreMouseEvents: (ignore) => ipcRenderer.send('set-ignore-mouse-events', ignore),
    showContextMenu: (x, y) => ipcRenderer.send('show-context-menu', x, y),
    updateMenuChecked: (label, checked) => ipcRenderer.send('update-menu-checked', label, checked),
    setSensitivity: (callback) => ipcRenderer.on('set-sensitivity', callback),
    updateSensitivity: (value) => ipcRenderer.send('update-sensitivity', value),
    getClipboardContent: () => ipcRenderer.invoke('get-clipboard-content'),
    
    // Configuration APIs
    getConfig: () => ipcRenderer.invoke('config:get'),
    setConfig: (partial) => ipcRenderer.invoke('config:set', partial),
    updateConfig: (config) => ipcRenderer.invoke('update-config', config),
    getFeatureFlags: () => ipcRenderer.invoke('get-feature-flags'),
    updateFeatureFlags: (flags) => ipcRenderer.invoke('update-feature-flags', flags),
    getAWSConfig: () => ipcRenderer.invoke('get-aws-config'),
    updateAWSConfig: (config) => ipcRenderer.invoke('update-aws-config', config),
    
    // Claude API
    askClaude: (text) => ipcRenderer.invoke('claude:ask', text),
    getHealth: () => ipcRenderer.invoke('health:get'),
    
    // Authentication APIs
    isLoggedIn: () => ipcRenderer.invoke('is-logged-in'),
    login: () => ipcRenderer.invoke('login'),
    logout: () => ipcRenderer.invoke('logout'),
    
    // Custom URL protocol handler
    handleAuthCallback: (callback) => ipcRenderer.on('auth-callback', (event, data) => callback(data)),
});
