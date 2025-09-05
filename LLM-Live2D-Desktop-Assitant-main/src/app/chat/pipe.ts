/**
 * Chat Pipeline Module
 * 
 * This module provides the chat pipeline that integrates the local and cloud components.
 * It handles the flow of messages between the user, the local components, and the cloud components.
 */

import { connectWS, WSHandle, Inbound, Outbound } from '../../infra/ws/wsClient';
import { getIdToken, isLoggedIn } from '../../infra/auth/noneAuth';
import { speak } from '../speech/ttsBridge';
import { transcribe } from '../speech/sttBridge';
import { getFeatureFlags } from '../../config/appConfig';

// Chat state
let wsClient: WSHandle | null = null;
let sessionId: string = generateSessionId();
let isConnecting = false;
let messageBuffer: string = '';
let isSpeaking = false;

// Event callbacks
type MessageCallback = (message: string, isComplete: boolean) => void;
type StatusCallback = (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void;

const messageCallbacks: MessageCallback[] = [];
const statusCallbacks: StatusCallback[] = [];

/**
 * Generate a unique session ID
 * @returns A unique session ID
 */
function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}

/**
 * Initialize the WebSocket connection
 * @returns A promise that resolves when the connection is established
 */
async function initializeWS(): Promise<void> {
  if (wsClient || isConnecting) {
    return;
  }

  isConnecting = true;
  updateStatus('connecting');

  try {
    wsClient = await connectWS(getIdToken);

    wsClient.onMessage(handleIncomingMessage);
    wsClient.onStatus(status => {
      if (status === 'open') {
        updateStatus('connected');
      } else if (status === 'closed') {
        updateStatus('disconnected');
      } else {
        updateStatus(status as 'connecting' | 'error');
      }
    });

    isConnecting = false;
  } catch (error) {
    console.error('Failed to initialize WebSocket:', error);
    isConnecting = false;
    updateStatus('error');
    throw error;
  }
}

/**
 * Handle incoming messages from the WebSocket
 * @param message The incoming message
 */
function handleIncomingMessage(message: Inbound): void {
  switch (message.type) {
    case 'assistant_text_delta':
      // Append the text to the buffer
      messageBuffer += message.text;
      
      // Notify callbacks about the new text
      messageCallbacks.forEach(cb => cb(messageBuffer, false));
      
      // Start speaking if not already speaking
      if (!isSpeaking && messageBuffer.length >= 30) {
        startSpeaking(messageBuffer);
      }
      break;
      
    case 'assistant_done':
      // Notify callbacks that the message is complete
      messageCallbacks.forEach(cb => cb(messageBuffer, true));
      
      // Reset the buffer
      messageBuffer = '';
      break;
      
    case 'error':
      console.error('WebSocket error:', message.message);
      break;
      
    case 'server_event':
      console.log('Server event:', message.name, message.data);
      break;
  }
}

/**
 * Start speaking the text
 * @param text The text to speak
 */
async function startSpeaking(text: string): Promise<void> {
  const flags = getFeatureFlags();
  
  // Check if TTS is enabled
  if (!flags.useLocalTTS && !flags.useCloudFallbacks) {
    return;
  }
  
  isSpeaking = true;
  
  try {
    const result = await speak(text);
    
    if (result.success && result.audioData) {
      // Play the audio
      // In a real implementation, this would play the audio through the existing audio system
      console.log(`Speaking text (${result.source}): ${text}`);
    } else {
      console.error('TTS failed:', result.error);
    }
  } catch (error) {
    console.error('Error in startSpeaking:', error);
  } finally {
    isSpeaking = false;
  }
}

/**
 * Update the connection status and notify listeners
 * @param status The new connection status
 */
function updateStatus(status: 'connecting' | 'connected' | 'disconnected' | 'error'): void {
  statusCallbacks.forEach(cb => cb(status));
}

/**
 * Send a text message to the WebSocket
 * @param text The text to send
 * @param meta Additional metadata to include with the message
 * @returns A promise that resolves when the message is sent
 */
export async function sendUserText(text: string, meta?: Record<string, any>): Promise<void> {
  if (!isLoggedIn()) {
    throw new Error('User is not authenticated');
  }
  
  // Initialize the WebSocket if not already initialized
  if (!wsClient) {
    await initializeWS();
  }
  
  if (!wsClient) {
    throw new Error('WebSocket is not initialized');
  }
  
  // Create the message
  const message: Outbound = {
    action: 'chat',
    text,
    sessionId,
    meta
  };
  
  // Send the message
  wsClient.send(message);
}

/**
 * Listen for speech and send it to the WebSocket
 * @returns A promise that resolves when the speech is sent
 */
export async function listenAndSend(): Promise<void> {
  const result = await transcribe(new ArrayBuffer(0));
  
  if (result.success && result.text) {
    await sendUserText(result.text);
  } else {
    console.error('STT failed:', result.error);
    throw result.error;
  }
}

/**
 * Register a callback for incoming messages
 * @param callback The callback function
 */
export function onMessage(callback: MessageCallback): void {
  messageCallbacks.push(callback);
}

/**
 * Register a callback for connection status changes
 * @param callback The callback function
 */
export function onStatus(callback: StatusCallback): void {
  statusCallbacks.push(callback);
}

/**
 * Close the WebSocket connection
 */
export function close(): void {
  if (wsClient) {
    wsClient.close();
    wsClient = null;
  }
  
  messageBuffer = '';
  updateStatus('disconnected');
}

/**
 * Check the connection status
 * @returns A promise that resolves to true if connected, false otherwise
 */
export async function checkConnection(): Promise<boolean> {
  try {
    if (!wsClient) {
      await initializeWS();
    }
    
    return !!wsClient;
  } catch (error) {
    console.error('Connection check failed:', error);
    return false;
  }
}
