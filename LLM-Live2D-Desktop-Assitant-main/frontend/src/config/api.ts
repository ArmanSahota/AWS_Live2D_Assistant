/**
 * API Configuration - Single Source of Truth
 * Handles environment-based URL configuration for development and production
 */

const isDevelopment = import.meta.env.DEV

export const API_CONFIG = {
  // Base URLs - Use proxy paths in development, direct URLs in production
  baseURL: isDevelopment 
    ? '/api'  // Proxy in development via Vite
    : import.meta.env.VITE_API_BASE_URL || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
  
  wsURL: isDevelopment
    ? '/ws'   // Proxy in development via Vite
    : import.meta.env.VITE_WS_BASE_URL || 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
    
  timeout: 10000,
  
  // Development flags
  isDevelopment,
  enableMockEndpoints: isDevelopment
}

export const ENDPOINTS = {
  // Health and system
  health: '/health',
  
  // Mock endpoints for development
  mockTTS: '/api/tts/mock',
  mockSTT: '/api/stt/mock',
  
  // WebSocket endpoints
  websocket: '/client-ws',
  echo: '/ws/echo',
  
  // Future API endpoints (to be implemented)
  tts: '/tts',
  stt: '/stt',
  config: '/config',
  models: '/models'
}

export const WS_MESSAGE_TYPES = {
  // Existing message types from current implementation
  FULL_TEXT: 'full-text',
  SET_MODEL: 'set-model',
  CONTROL: 'control',
  CONFIG_SWITCHED: 'config-switched',
  ERROR: 'error',
  
  // Audio pipeline
  MIC_AUDIO_DATA: 'mic-audio-data',
  MIC_AUDIO_END: 'mic-audio-end',
  TEXT_INPUT: 'text-input',
  INTERRUPT_SIGNAL: 'interrupt-signal',
  
  // Configuration
  FETCH_CONFIGS: 'fetch-configs',
  CONFIG_FILES: 'config-files',
  SWITCH_CONFIG: 'switch-config',
  
  // Backgrounds
  FETCH_BACKGROUNDS: 'fetch-backgrounds',
  BACKGROUND_FILES: 'background-files',
  
  // Echo (for testing)
  ECHO: 'echo'
}

/**
 * Get the full URL for an endpoint
 */
export function getEndpointURL(endpoint: string): string {
  return `${API_CONFIG.baseURL}${endpoint}`
}

/**
 * Get the full WebSocket URL for an endpoint
 */
export function getWebSocketURL(endpoint: string): string {
  return `${API_CONFIG.wsURL}${endpoint}`
}

/**
 * Development helper to log API configuration
 */
export function logAPIConfig(): void {
  if (API_CONFIG.isDevelopment) {
    console.log('🔧 API Configuration:', {
      baseURL: API_CONFIG.baseURL,
      wsURL: API_CONFIG.wsURL,
      isDevelopment: API_CONFIG.isDevelopment,
      enableMockEndpoints: API_CONFIG.enableMockEndpoints
    })
  }
}