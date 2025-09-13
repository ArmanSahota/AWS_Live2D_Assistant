/**
 * Claude Client Module
 * 
 * This module provides a client for the Claude API.
 * It handles the communication with the Claude endpoint.
 */

import { getAWSConfig } from '../config/appConfig';
import { ClaudeRequestBody, ClaudeResponse } from '../types/http';

// Cache for the last Claude response
let lastResponse: ClaudeResponse | null = null;

// Request queue to prevent multiple simultaneous requests
const requestQueue: Array<() => Promise<string>> = [];
let isProcessing = false;

/**
 * Ask Claude a question
 * @param text The text to send to Claude
 * @returns A promise that resolves to Claude's response
 */
export async function askClaude(text: string): Promise<string> {
  // Add the request to the queue and process it
  return new Promise<string>((resolve, reject) => {
    requestQueue.push(async () => {
      try {
        const response = await sendClaudeRequest(text);
        resolve(response);
        return response;
      } catch (error) {
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
async function processQueue(): Promise<void> {
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
 * @param text The text to send to Claude
 * @returns A promise that resolves to Claude's response
 */
async function sendClaudeRequest(text: string): Promise<string> {
  const config = getAWSConfig();
  
  if (!config.httpBase) {
    throw new Error('HTTP base URL is not configured');
  }
  
  const startTime = Date.now();
  console.log(`[Claude] Sending request: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`);
  
  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    };
    
    // Add authorization if available
    if (config.authToken) {
      headers['Authorization'] = `Bearer ${config.authToken}`;
    }
    
    // Build the request body
    const requestBody: ClaudeRequestBody = {
      text
    };
    
    // Send the request
    const response = await fetch(`${config.httpBase}/claude`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody)
    });
    
    // Check for errors
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Claude request failed: ${response.status} ${response.statusText}. ${errorText}`);
    }
    
    // Parse the response
    const data: ClaudeResponse = await response.json();
    lastResponse = data;
    
    // Log the response time
    const duration = Date.now() - startTime;
    console.log(`[Claude] Response received in ${duration}ms`);
    
    return data.reply;
  } catch (error) {
    console.error('Error in Claude request:', error);
    throw error;
  }
}

/**
 * Get the last Claude response
 * @returns The last Claude response, or null if there was no response yet
 */
export function getLastClaudeResponse(): ClaudeResponse | null {
  return lastResponse;
}
