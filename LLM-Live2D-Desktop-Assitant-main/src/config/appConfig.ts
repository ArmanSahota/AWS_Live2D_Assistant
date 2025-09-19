/**
 * Application configuration module
 * 
 * This module provides typed configuration for the application, merging:
 * - Environment variables
 * - Persisted user overrides from electron-store
 */

import Store from 'electron-store';
import { app } from 'electron';

// Define the feature flags interface
export interface FeatureFlags {
  useLocalTTS: boolean;
  useLocalSTT: boolean;
  useCloudFallbacks: boolean;
}

// Define the AWS configuration interface
export interface AWSConfig {
  region: string;
  wsUrl: string;
  httpBase: string;
  httpBaseUrl: string;
  authToken?: string;
  cognitoUserPoolId: string;
  cognitoClientId: string;
  cognitoDomain: string;
  modelId: string;
}

// Define the application configuration interface
export interface AppConfig {
  httpBase: string;
  features: FeatureFlags;
  aws: AWSConfig;
}

// Create a store for persisted user preferences
const store = new Store({
  name: 'config', // This will be stored in ~/.config/<app-name>/config.json
  defaults: {
    httpBase: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
    features: {
      useLocalTTS: true,
      useLocalSTT: true,
      useCloudFallbacks: true,
    },
    aws: {
      region: process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.VITE_WS_URL || 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
      httpBase: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      httpBaseUrl: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      cognitoUserPoolId: process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.VITE_COGNITO_DOMAIN || '',
      modelId: process.env.VITE_MODEL_ID || 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    }
  }
});

/**
 * Read the application configuration, merging environment variables and user preferences
 * @returns The merged application configuration
 */
export function readConfig(): AppConfig {
  // Get the environment variables
  const envConfig: AppConfig = {
    httpBase: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
    features: {
      useLocalTTS: process.env.VITE_FEATURE_USE_LOCAL_TTS === 'true' || true,
      useLocalSTT: process.env.VITE_FEATURE_USE_LOCAL_STT === 'true' || true,
      useCloudFallbacks: process.env.VITE_FEATURE_USE_CLOUD_FALLBACKS === 'true' || true,
    },
    aws: {
      region: process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.VITE_WS_URL || 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
      httpBase: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      httpBaseUrl: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      cognitoUserPoolId: process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.VITE_COGNITO_DOMAIN || '',
      modelId: process.env.VITE_MODEL_ID || 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    }
  };

  // Get the stored user preferences
  const storedConfig = store.get('config') as Partial<AppConfig> | undefined;

  // Merge the configurations, with user preferences taking precedence
  const mergedConfig: AppConfig = {
    httpBase: storedConfig?.httpBase || envConfig.httpBase,
    features: {
      ...envConfig.features,
      ...(storedConfig?.features || {}),
    },
    aws: {
      ...envConfig.aws,
      ...(storedConfig?.aws || {}),
    }
  };

  return mergedConfig;
}

/**
 * Update the user preferences
 * @param config The new configuration to store
 */
export function updateConfig(config: Partial<AppConfig>): void {
  // Get the current stored configuration
  const currentConfig = store.get('config') as Partial<AppConfig> | undefined || {};

  // Merge the new configuration with the current one
  const newConfig = {
    ...currentConfig,
    ...config,
    features: {
      ...(currentConfig.features || {}),
      ...(config.features || {}),
    },
    aws: {
      ...(currentConfig.aws || {}),
      ...(config.aws || {}),
    }
  };

  // Store the new configuration
  store.set('config', newConfig);
}

/**
 * Save configuration with partial updates
 * @param partial Partial configuration to update
 */
export function saveConfig(partial: Partial<AppConfig>): void {
  updateConfig(partial);
}

/**
 * Get the current feature flags
 * @returns The current feature flags
 */
export function getFeatureFlags(): FeatureFlags {
  return readConfig().features;
}

/**
 * Update the feature flags
 * @param flags The new feature flags
 */
export function updateFeatureFlags(flags: Partial<FeatureFlags>): void {
  // We're only updating the config with partial flags, not replacing the entire features object
  updateConfig({ features: flags as any });
}

/**
 * Get the current AWS configuration
 * @returns The current AWS configuration
 */
export function getAWSConfig(): AWSConfig {
  return readConfig().aws;
}

/**
 * Update the AWS configuration
 * @param config The new AWS configuration
 */
export function updateAWSConfig(config: Partial<AWSConfig>): void {
  // We're only updating the config with partial AWS settings, not replacing the entire aws object
  updateConfig({ aws: config as any });
}
