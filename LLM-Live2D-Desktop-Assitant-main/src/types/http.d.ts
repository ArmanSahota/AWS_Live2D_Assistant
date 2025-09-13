/**
 * HTTP-related type definitions
 */

// Claude API request body
export interface ClaudeRequestBody {
  text: string;
  options?: {
    temperature?: number;
    maxTokens?: number;
    stopSequences?: string[];
  };
}

// Claude API response
export interface ClaudeResponse {
  reply: string;
  metadata?: {
    usage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    };
    finishReason?: string;
  };
}

// Health check response
export interface HealthResponse {
  status: string;
  version: string;
  services: {
    [key: string]: {
      status: string;
      message?: string;
    };
  };
}
