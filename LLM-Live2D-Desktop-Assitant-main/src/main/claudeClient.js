/**
 * Claude HTTP Client Module
 * 
 * This module provides a client for interacting with the Claude API over HTTP.
 * It handles request formatting, response parsing, and error handling.
 */

const { readConfig } = require('../config/appConfig');

// Cache for the last Claude response
let lastResponse = null;

// Request queue to prevent multiple simultaneous requests
const requestQueue = [];
let isProcessing = false;

/**
 * Ask Claude a question and get a response
 * @param {string} text The text to send to Claude
 * @param {Object} opts Options for the request
 * @returns {Promise<string>} A promise that resolves to the reply text
 */
async function askClaude(text, opts = {}) {
  // Add the request to the queue and process it
  return new Promise((resolve, reject) => {
    requestQueue.push(async () => {
      try {
        const response = await sendClaudeRequest(text, opts);
        resolve(response);
        return response;
      } catch (error) {
        console.error('Claude request failed:', error);
        reject(error);
        throw error;
      }
    });
    
    processQueue();
  });
}

/**
 * Process the request queue
 */
async function processQueue() {
  if (isProcessing || requestQueue.length === 0) {
    return;
  }
  
  isProcessing = true;
  
  try {
    const request = requestQueue.shift();
    if (request) {
      await request();
    }
  } catch (error) {
    console.error('Error processing Claude request:', error);
  } finally {
    isProcessing = false;
    
    // Process the next request in the queue
    if (requestQueue.length > 0) {
      processQueue();
    }
  }
}

/**
 * Send a request to the Claude API
 * @param {string} text The text to send to Claude
 * @param {Object} opts Options for the request
 * @returns {Promise<string>} A promise that resolves to Claude's response
 */
async function sendClaudeRequest(text, opts = {}) {
  const config = readConfig();
  const httpBase = config.httpBase;
  
  if (!httpBase) {
    throw new Error('HTTP base URL is not configured');
  }
  
  const url = `${httpBase}/claude`;
  const timeoutMs = opts.timeoutMs || 30000; // Default timeout: 30 seconds
  
  console.log(`[Claude] Sending request to ${url}`);
  console.log(`[Claude] Request text: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`);
  
  // Create an AbortController for timeout handling
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    // Prepare the request
    const request = { text };
    
    // Send the request
    const startTime = Date.now();
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
    
    // Clear the timeout
    clearTimeout(timeoutId);
    
    // Check for errors
    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}`;
      
      try {
        // Try to parse the error response as JSON
        const errorData = await response.json();
        if (errorData.error) {
          errorMessage = `HTTP error ${response.status}: ${errorData.error}`;
        }
      } catch (e) {
        // If parsing fails, use the status text
        errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      }
      
      console.error(`[Claude] ${errorMessage}`);
      throw new Error(errorMessage);
    }
    
    // Parse the response
    const data = await response.json();
    
    // Check if the reply is missing
    if (!data.reply) {
      console.error('[Claude] Invalid response: missing reply field');
      throw new Error('Invalid response: missing reply field');
    }
    
    // Cache the response
    lastResponse = data;
    
    // Log the response time
    const duration = Date.now() - startTime;
    console.log(`[Claude] Response received in ${duration}ms`);
    console.log(`[Claude] Response: ${data.reply.substring(0, 100)}${data.reply.length > 100 ? '...' : ''}`);
    
    return data.reply;
  } catch (error) {
    // Clear the timeout if there was an error
    clearTimeout(timeoutId);
    
    // Handle abort errors
    if (error.name === 'AbortError') {
      console.error('[Claude] Request timed out');
      throw new Error('Request timed out');
    }
    
    // Re-throw other errors
    console.error(`[Claude] Error: ${error.message}`);
    throw error;
  }
}

/**
 * Get the last Claude response
 * @returns The last Claude response, or null if there was no response yet
 */
function getLastClaudeResponse() {
  return lastResponse;
}

module.exports = { askClaude, getLastClaudeResponse };
