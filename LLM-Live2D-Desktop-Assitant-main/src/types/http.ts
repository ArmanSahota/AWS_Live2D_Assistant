/**
 * HTTP API Types
 * 
 * This module defines types for HTTP API requests and responses.
 */

/**
 * Claude API request type
 */
export type ClaudeRequest = { 
  text: string 
};

/**
 * Claude API response type
 */
export type ClaudeResponse = { 
  reply: string 
};

/**
 * Health check response type
 */
export type HealthResponse = { 
  status: string 
};
