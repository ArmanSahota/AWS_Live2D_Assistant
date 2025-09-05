/**
 * Claude HTTP Client Module
 * 
 * This module provides a client for interacting with the Claude API over HTTP.
 * It handles request formatting, response parsing, and error handling.
 */

import { readConfig } from '../config/appConfig';
import { ClaudeRequest, ClaudeResponse } from '../types/http';

/**
 * Ask Claude a question and get a response
 * @param text The text to send to Claude
 * @param opts Options for the request
 * @returns A promise that resolves to the reply text
 */
export async function askClaude(text: string, opts?: { timeoutMs?: number }): Promise<string> {
  const config = readConfig();
  const httpBase = config.httpBase;
  
  if (!httpBase) {
    throw new Error('HTTP base URL is not configured');
  }
  
  const url = `${httpBase}/claude`;
  const timeoutMs = opts?.timeoutMs || 30000; // Default timeout: 30 seconds
  
  // Create an AbortController for timeout handling
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    // Prepare the request
    const request: ClaudeRequest = { text };
    
    // Send the request
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
      
      throw new Error(errorMessage);
    }
    
    // Parse the response
    const data = await response.json() as ClaudeResponse;
    
    // Check if the reply is missing
    if (!data.reply) {
      throw new Error('Invalid response: missing reply field');
    }
    
    return data.reply;
  } catch (error) {
    // Clear the timeout if there was an error
    clearTimeout(timeoutId);
    
    // Handle abort errors
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    
    // Re-throw other errors
    throw error;
  }
}
