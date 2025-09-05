/**
 * HTTP API Client Module
 * 
 * This module provides functions for interacting with the AWS HTTP API endpoints.
 * It handles authentication, request formatting, and response parsing.
 */

import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { getAuthHeaders, isLoggedIn } from '../auth/noneAuth';
import { getAWSConfig } from '../../config/appConfig';

// Create an axios instance with default configuration
const api = axios.create({
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Add authentication headers to a request config
 * @param config The axios request config
 * @returns The config with authentication headers
 */
async function withAuth(config: AxiosRequestConfig): Promise<AxiosRequestConfig> {
  if (!isLoggedIn()) {
    throw new Error('User is not authenticated');
  }

  const headers = await getAuthHeaders();
  return {
    ...config,
    headers: {
      ...config.headers,
      ...headers,
    },
  };
}

/**
 * Get the base URL for API requests
 * @returns The base URL
 */
function getBaseUrl(): string {
  const config = getAWSConfig();
  return config.httpBaseUrl;
}

/**
 * Check the health of the API
 * @returns A promise that resolves to the health status
 */
export async function getHealth(): Promise<{ status: string; latency: number }> {
  const startTime = Date.now();
  
  try {
    const response = await api.get(`${getBaseUrl()}/health`);
    const latency = Date.now() - startTime;
    
    return {
      status: response.data.status || 'ok',
      latency,
    };
  } catch (error) {
    console.error('Health check failed:', error);
    return {
      status: 'error',
      latency: Date.now() - startTime,
    };
  }
}

/**
 * Get a pre-signed URL for uploading a file
 * @param filename The name of the file to upload
 * @returns A promise that resolves to the upload URL
 */
export async function getUploadUrl(filename: string): Promise<string> {
  if (!isLoggedIn()) {
    throw new Error('User is not authenticated');
  }

  const config = await withAuth({
    method: 'GET',
    url: `${getBaseUrl()}/upload-url`,
    params: { filename },
  });

  const response = await api(config);
  return response.data.url;
}

/**
 * Use the TTS fallback API to convert text to speech
 * @param text The text to convert to speech
 * @param voice The voice to use
 * @returns A promise that resolves to the audio data
 */
export async function ttsFallback(text: string, voice: string = 'default'): Promise<ArrayBuffer> {
  if (!isLoggedIn()) {
    throw new Error('User is not authenticated');
  }

  const config = await withAuth({
    method: 'POST',
    url: `${getBaseUrl()}/tts`,
    data: { text, voice },
    responseType: 'arraybuffer',
  });

  const response = await api(config);
  return response.data;
}

/**
 * Handle API errors
 * @param error The error object
 * @throws A formatted error
 */
function handleApiError(error: any): never {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message;
    
    if (status === 401 || status === 403) {
      throw new Error(`Authentication error: ${message}`);
    } else if (status === 404) {
      throw new Error(`Resource not found: ${message}`);
    } else {
      throw new Error(`API error (${status}): ${message}`);
    }
  }
  
  throw error;
}

// Add response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: any) => {
    console.error('API request failed:', error);
    return Promise.reject(handleApiError(error));
  }
);
