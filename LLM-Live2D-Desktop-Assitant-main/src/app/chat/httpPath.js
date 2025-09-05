/**
 * HTTP Chat Path Module (JavaScript version)
 * 
 * This module provides the HTTP-based chat pipeline for communicating with Claude.
 * It handles sending user messages, receiving assistant responses, and updating the UI.
 */

const { getFeatureFlags } = require('../../config/appConfig');

// Chat state
let transcript = [];
let inFlightRequest = null;
let isSpeaking = false;

// Event callbacks
const messageCallbacks = [];
const errorCallbacks = [];

/**
 * Send a user message to Claude via HTTP
 * @param {string} text The text to send
 * @returns {Promise<void>} A promise that resolves when the message is processed
 */
async function sendUserTextHTTP(text) {
  // Validate input
  if (!text || !text.trim()) {
    throw new Error('Message cannot be empty');
  }

  // Cancel any in-flight request
  if (inFlightRequest) {
    inFlightRequest.abort();
    inFlightRequest = null;
  }

  try {
    // Add user message to transcript
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };
    
    transcript.push(userMessage);
    notifyMessageCallbacks(userMessage, true);

    console.log(`Sending message to Claude: ${text}`);

    // Send the message to Claude
    const reply = await window.api.askClaude(text);

    console.log(`Received reply from Claude: ${reply}`);

    // Add assistant message to transcript
    const assistantMessage = {
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
 * @param {Function} callback The callback function
 */
function onMessage(callback) {
  messageCallbacks.push(callback);
  
  // Send existing transcript to the new callback
  transcript.forEach(message => callback(message, false));
}

/**
 * Register a callback for errors
 * @param {Function} callback The callback function
 */
function onError(callback) {
  errorCallbacks.push(callback);
}

/**
 * Notify all message callbacks about a new message
 * @param {Object} message The message
 * @param {boolean} isNew Whether the message is new
 */
function notifyMessageCallbacks(message, isNew) {
  messageCallbacks.forEach(callback => callback(message, isNew));
}

/**
 * Notify all error callbacks about an error
 * @param {Error} error The error
 */
function notifyErrorCallbacks(error) {
  errorCallbacks.forEach(callback => callback(error));
}

/**
 * Get the current transcript
 * @returns {Array} The transcript
 */
function getTranscript() {
  return [...transcript];
}

/**
 * Clear the transcript
 */
function clearTranscript() {
  transcript = [];
}

// Export the functions
module.exports = {
  sendUserTextHTTP,
  onMessage,
  onError,
  getTranscript,
  clearTranscript
};
