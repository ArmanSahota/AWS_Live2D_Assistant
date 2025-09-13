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

export type ClaudeRequestBody = ClaudeRequest;

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

/**
 * AWS Config type
 */
export interface AWSConfig {
  httpBase: string;
  authToken?: string;
  region?: string;
  apiKey?: string;
  bedrock?: {
    modelId?: string;
  };
}
