/**
 * HTTP Chat Path Module
 * 
 * This module provides the HTTP-based chat pipeline for communicating with Claude.
 * It handles sending user messages, receiving assistant responses, and updating the UI.
 */

import { getFeatureFlags } from '../../config/appConfig';
import { speak } from '../speech/ttsBridge';

// Define the message type
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

// Chat state
let transcript: ChatMessage[] = [];
let inFlightRequest: AbortController | null = null;

// Event callbacks
type MessageCallback = (message: ChatMessage, isNew: boolean) => void;
type ErrorCallback = (error: Error) => void;

const messageCallbacks: MessageCallback[] = [];
const errorCallbacks: ErrorCallback[] = [];

/**
 * Send a user message to Claude via HTTP
 * @param text The text to send
 * @returns A promise that resolves when the message is processed
 */
export async function sendUserTextHTTP(text: string): Promise<void> {
  // Validate input
  if (!text || !text.trim()) {
    throw new Error('Message cannot be empty');
  }

  // Cancel any in-flight request
  if (inFlightRequest) {
    inFlightRequest.abort();
    inFlightRequest = null;
  }

  // Create a new abort controller for this request
  inFlightRequest = new AbortController();

  try {
    // Add user message to transcript
    const userMessage: ChatMessage = {
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };
    
    transcript.push(userMessage);
    notifyMessageCallbacks(userMessage, true);

    // Send the message to Claude
    const reply = await window.api.askClaude(text);

    // Add assistant message to transcript
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: reply,
      timestamp: Date.now(),
    };
    
    transcript.push(assistantMessage);
    notifyMessageCallbacks(assistantMessage, true);

    // Speak the reply if local TTS is enabled
    const flags = getFeatureFlags();
    if (flags.useLocalTTS) {
      await speak(reply);
    }
  } catch (error) {
    console.error('Error in HTTP chat path:', error);
    
    // Notify error callbacks
    const errorMessage = error instanceof Error ? error.message : String(error);
    notifyErrorCallbacks(new Error(`Cloud request failed: ${errorMessage}`));
  } finally {
    inFlightRequest = null;
  }
}

/**
 * Register a callback for new messages
 * @param callback The callback function
 */
export function onMessage(callback: MessageCallback): void {
  messageCallbacks.push(callback);
  
  // Send existing transcript to the new callback
  transcript.forEach(message => callback(message, false));
}

/**
 * Register a callback for errors
 * @param callback The callback function
 */
export function onError(callback: ErrorCallback): void {
  errorCallbacks.push(callback);
}

/**
 * Notify all message callbacks about a new message
 * @param message The message
 * @param isNew Whether the message is new
 */
function notifyMessageCallbacks(message: ChatMessage, isNew: boolean): void {
  messageCallbacks.forEach(callback => callback(message, isNew));
}

/**
 * Notify all error callbacks about an error
 * @param error The error
 */
function notifyErrorCallbacks(error: Error): void {
  errorCallbacks.forEach(callback => callback(error));
}

/**
 * Get the current transcript
 * @returns The transcript
 */
export function getTranscript(): ChatMessage[] {
  return [...transcript];
}

/**
 * Clear the transcript
 */
export function clearTranscript(): void {
  transcript = [];
}
