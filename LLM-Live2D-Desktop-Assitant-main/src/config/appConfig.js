/**
 * Application configuration module (CommonJS version)
 * 
 * This module provides configuration for the application, merging:
 * - Environment variables
 * - Persisted user overrides from electron-store
 */

const Store = require('electron-store');
const { app } = require('electron');

// Create a store for persisted user preferences
const store = new Store({
  name: 'config', // This will be stored in ~/.config/<app-name>/config.json
  defaults: {
    httpBase: process.env.VITE_HTTP_BASE || '',
    features: {
      useLocalTTS: true,
      useLocalSTT: true,
      useCloudFallbacks: true,
    },
    aws: {
      region: process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.VITE_WS_URL || '',
      httpBaseUrl: process.env.VITE_HTTP_BASE || '',
      cognitoUserPoolId: process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.VITE_COGNITO_DOMAIN || '',
    }
  }
});

/**
 * Read the application configuration, merging environment variables and user preferences
 * @returns The merged application configuration
 */
function readConfig() {
  // Get the environment variables
  const envConfig = {
    httpBase: process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
    features: {
      useLocalTTS: process.env.VITE_FEATURE_USE_LOCAL_TTS === 'true' || true,
      useLocalSTT: process.env.VITE_FEATURE_USE_LOCAL_STT === 'true' || true,
      useCloudFallbacks: process.env.VITE_FEATURE_USE_CLOUD_FALLBACKS === 'true' || true,
    },
    aws: {
      region: process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.VITE_WS_URL || '',
      httpBaseUrl: process.env.VITE_HTTP_BASE || '',
      cognitoUserPoolId: process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.VITE_COGNITO_DOMAIN || '',
    }
  };

  // Get the stored user preferences
  const storedConfig = store.get('config') || {};

  // Merge the configurations, with user preferences taking precedence
  const mergedConfig = {
    httpBase: storedConfig.httpBase || envConfig.httpBase,
    features: {
      ...envConfig.features,
      ...(storedConfig.features || {}),
    },
    aws: {
      ...envConfig.aws,
      ...(storedConfig.aws || {}),
    }
  };

  return mergedConfig;
}

/**
 * Update the user preferences
 * @param {Object} config The new configuration to store
 */
function updateConfig(config) {
  // Get the current stored configuration
  const currentConfig = store.get('config') || {};

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
 * Get the current feature flags
 * @returns The current feature flags
 */
function getFeatureFlags() {
  return readConfig().features;
}

/**
 * Update the feature flags
 * @param {Object} flags The new feature flags
 */
function updateFeatureFlags(flags) {
  // We're only updating the config with partial flags, not replacing the entire features object
  updateConfig({ features: flags });
}

/**
 * Get the current AWS configuration
 * @returns The current AWS configuration
 */
function getAWSConfig() {
  return readConfig().aws;
}

/**
 * Update the AWS configuration
 * @param {Object} config The new AWS configuration
 */
function updateAWSConfig(config) {
  // We're only updating the config with partial AWS settings, not replacing the entire aws object
  updateConfig({ aws: config });
}

/**
 * Save configuration with partial updates
 * @param {Object} partial Partial configuration to update
 */
function saveConfig(partial) {
  updateConfig(partial);
}

module.exports = {
  readConfig,
  updateConfig,
  saveConfig,
  getFeatureFlags,
  updateFeatureFlags,
  getAWSConfig,
  updateAWSConfig
};
