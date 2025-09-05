/**
 * Electron Type Declarations
 * 
 * This module provides type declarations for Electron-specific APIs.
 */

interface Window {
  api: {
    // Claude API
    askClaude: (text: string) => Promise<string>;
    getHealth: () => Promise<{ status: string; latency: number }>;
    
    // Configuration APIs
    getConfig: () => Promise<any>;
    setConfig: (partial: any) => Promise<any>;
    updateConfig: (config: any) => Promise<any>;
    getFeatureFlags: () => Promise<any>;
    updateFeatureFlags: (flags: any) => Promise<any>;
    getAWSConfig: () => Promise<any>;
    updateAWSConfig: (config: any) => Promise<any>;
    
    // Authentication APIs
    isLoggedIn: () => Promise<boolean>;
    login: () => Promise<boolean>;
    logout: () => Promise<boolean>;
    
    // UI control APIs
    onToggleSubtitles: (callback: (data: any) => void) => void;
    onToggleMicrophone: (callback: (data: any) => void) => void;
    onToggleInterruption: (callback: (data: any) => void) => void;
    onToggleWakeUp: (callback: (data: any) => void) => void;
    sendConfigFiles: (files: string[]) => void;
    onSwitchConfig: (callback: (data: any) => void) => void;
    setIgnoreMouseEvents: (ignore: boolean) => void;
    showContextMenu: (x: number, y: number) => void;
    updateMenuChecked: (label: string, checked: boolean) => void;
    setSensitivity: (callback: (data: any) => void) => void;
    updateSensitivity: (value: number) => void;
    getClipboardContent: () => Promise<{ text: string; image: string | null }>;
    
    // Custom URL protocol handler
    handleAuthCallback: (callback: (data: any) => void) => void;
  };
}
