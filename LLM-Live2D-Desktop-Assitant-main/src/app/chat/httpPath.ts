/**
 * HTTP Chat Path Module
 * 
 * This module provides functionality for sending messages to Claude via HTTP
 * and handling responses, including TTS playback of replies.
 */

import { speak } from '../speech/ttsBridge';
import { listenOnce } from '../speech/sttBridge';
import { getFeatureFlags } from '../../config/appConfig';

// Message type for chat messages
interface ChatMessage {
  type: 'user' | 'assistant';
  text: string;
  timestamp: number;
  id: string;
}

// Chat history
const chatHistory: ChatMessage[] = [];

// Status callbacks
type StatusCallback = (status: string, details?: any) => void;
const statusCallbacks: StatusCallback[] = [];

// Current status
let currentStatus = 'idle';

/**
 * Generate a unique ID for chat messages
 * @returns A unique ID
 */
function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

/**
 * Update the chat status and notify listeners
 * @param status The new status
 * @param details Optional details about the status
 */
function updateStatus(status: string, details?: any): void {
  if (currentStatus !== status) {
    console.log(`[HTTP Chat] Status changed from ${currentStatus} to ${status}`, details || '');
    currentStatus = status;
    statusCallbacks.forEach(callback => callback(status, details));
  }
}

/**
 * Register a status callback
 * @param callback The callback function
 */
export function onStatus(callback: StatusCallback): void {
  statusCallbacks.push(callback);
  // Call immediately with current status
  callback(currentStatus);
}

/**
 * Add a message to the chat history
 * @param type The type of message (user or assistant)
 * @param text The message text
 */
function addMessage(type: 'user' | 'assistant', text: string): ChatMessage {
  const message: ChatMessage = {
    type,
    text,
    timestamp: Date.now(),
    id: generateId()
  };
  
  chatHistory.push(message);
  return message;
}

/**
 * Get the chat history
 * @returns The chat history
 */
export function getChatHistory(): ChatMessage[] {
  return [...chatHistory];
}

/**
 * Clear the chat history
 */
export function clearChatHistory(): void {
  chatHistory.length = 0;
}

/**
 * Send user text message via HTTP and process the response
 * @param text The user's text message
 * @returns A promise that resolves when the message has been processed
 */
export async function sendUserTextHTTP(text: string): Promise<void> {
  if (!text || text.trim().length === 0) {
    console.warn('Attempted to send empty message');
    return;
  }
  
  // Add user message to chat history
  const userMessage = addMessage('user', text);
  
  // Add message to UI
  addMessageToUI(userMessage);
  
  // Update status
  updateStatus('sending');
  
  try {
    // Send message to Claude via IPC
    const reply = await window.api.askClaude(text);
    
    // Update status
    updateStatus('processing');
    
    // Add assistant message to chat history
    const assistantMessage = addMessage('assistant', reply);
    
    // Add message to UI
    addMessageToUI(assistantMessage);
    
    // Check if TTS is enabled
    const flags = getFeatureFlags();
    if (flags.useLocalTTS) {
      try {
        // Update status
        updateStatus('speaking');
        
        // Speak the reply
        const result = await speak(reply);
        
        if (!result.success) {
          console.error('TTS failed:', result.error);
        }
      } catch (error) {
        console.error('Error during TTS:', error);
      }
    }
    
    // Update status
    updateStatus('idle');
  } catch (error) {
    console.error('Error sending message:', error);
    
    // Show error message in UI
    const errorMessage = 'Failed to get a response from Claude. Please try again.';
    const assistantMessage = addMessage('assistant', errorMessage);
    addMessageToUI(assistantMessage);
    
    // Update status
    updateStatus('error', { error });
  }
}

/**
 * Listen for user speech, transcribe it, and send to Claude
 * @returns A promise that resolves when the speech has been processed
 */
export async function listenAndSendHTTP(): Promise<void> {
  try {
    // Update status
    updateStatus('listening');
    
    // Listen for speech
    const result = await listenOnce();
    
    if (!result.success || !result.text) {
      console.error('STT failed:', result.error);
      updateStatus('error', { error: result.error });
      return;
    }
    
    // Send the transcribed text to Claude
    await sendUserTextHTTP(result.text);
  } catch (error) {
    console.error('Error in speech recognition:', error);
    updateStatus('error', { error });
  }
}

/**
 * Add a message to the UI
 * @param message The message to add
 */
function addMessageToUI(message: ChatMessage): void {
  // In a real implementation, this would update the UI
  // For now, we'll just log the message
  console.log(`[${message.type}] ${message.text}`);
  
  // Add the message to the chat container
  const chatContainer = document.getElementById('chat-container');
  if (chatContainer) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${message.type}`;
    messageElement.textContent = message.text;
    chatContainer.appendChild(messageElement);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } else {
    console.warn('Chat container not found');
  }
}
