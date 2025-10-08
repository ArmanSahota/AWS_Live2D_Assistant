/**
 * Application configuration module (CommonJS version)
 * 
 * This module provides configuration for the application, merging:
 * - Environment variables
 * - Persisted user overrides from electron-store
 */

const Store = require('electron-store');
const { app } = require('electron');
const path = require('path');
const fs = require('fs');

// Helper function to properly parse boolean values
function defBool(value, defaultValue) {
  if (value === 'true') return true;
  if (value === 'false') return false;
  return defaultValue;
}

// Log the configuration on startup
function logConfig(config) {
  console.log('=== Application Configuration ===');
  console.log(`HTTP Base: ${config.httpBase || '(not set)'}`);
  console.log('Feature Flags:');
  Object.entries(config.features).forEach(([key, value]) => {
    console.log(`  ${key}: ${value}`);
  });
  console.log('AWS Config:');
  console.log(`  Region: ${config.aws.region}`);
  console.log(`  HTTP Base URL: ${config.aws.httpBaseUrl || '(not set)'}`);
  console.log('===============================');
}

// Create a store for persisted user preferences
const store = new Store({
  name: 'config', // This will be stored in ~/.config/<app-name>/config.json
  defaults: {
    httpBase: process.env.HTTP_BASE || process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
    features: {
      useLocalTTS: defBool(process.env.FEATURE_USE_LOCAL_TTS, true),
      useLocalSTT: defBool(process.env.FEATURE_USE_LOCAL_STT, true),
      useCloudFallbacks: defBool(process.env.FEATURE_USE_CLOUD_FALLBACKS, true),
      useLocalWS: defBool(process.env.FEATURE_USE_LOCAL_WS, false),
      useVision: defBool(process.env.FEATURE_USE_VISION, false),
    },
    vision: {
      enabled: defBool(process.env.VISION_ENABLED, false),
      captureMode: process.env.VISION_CAPTURE_MODE || 'manual', // 'manual', 'speech-triggered', 'periodic'
      captureQuality: parseFloat(process.env.VISION_CAPTURE_QUALITY || '0.8'),
      resolution: process.env.VISION_RESOLUTION || '1280x720',
      periodicInterval: parseInt(process.env.VISION_PERIODIC_INTERVAL || '30000'),
      compressionEnabled: defBool(process.env.VISION_COMPRESSION_ENABLED, true),
      confidenceThreshold: parseFloat(process.env.VISION_CONFIDENCE_THRESHOLD || '0.7'),
      maxImageSize: parseInt(process.env.VISION_MAX_IMAGE_SIZE || '1048576'), // 1MB
      rateLimitMs: parseInt(process.env.VISION_RATE_LIMIT_MS || '5000'), // 5 seconds
      categories: {
        automotive: defBool(process.env.VISION_CATEGORY_AUTOMOTIVE, true),
        electronics: defBool(process.env.VISION_CATEGORY_ELECTRONICS, true),
        tools: defBool(process.env.VISION_CATEGORY_TOOLS, true),
        appliances: defBool(process.env.VISION_CATEGORY_APPLIANCES, true),
        medical: defBool(process.env.VISION_CATEGORY_MEDICAL, false)
      },
      analysis: {
        includeRepairInfo: defBool(process.env.VISION_INCLUDE_REPAIR_INFO, true),
        includeCostEstimates: defBool(process.env.VISION_INCLUDE_COST_ESTIMATES, true),
        includeSafetyWarnings: defBool(process.env.VISION_INCLUDE_SAFETY_WARNINGS, true),
        includeSpecifications: defBool(process.env.VISION_INCLUDE_SPECIFICATIONS, true),
        detailLevel: process.env.VISION_DETAIL_LEVEL || 'comprehensive' // 'basic', 'detailed', 'comprehensive'
      }
    },
    aws: {
      region: process.env.AWS_REGION || process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.WS_URL || process.env.VITE_WS_URL || 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
      httpBaseUrl: process.env.HTTP_BASE || process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      cognitoUserPoolId: process.env.COGNITO_USER_POOL_ID || process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.COGNITO_CLIENT_ID || process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.COGNITO_DOMAIN || process.env.VITE_COGNITO_DOMAIN || '',
      modelId: process.env.MODEL_ID || process.env.VITE_MODEL_ID || 'anthropic.claude-3-7-sonnet-20250219-v1:0',
      // RAG Configuration
      documentsBucketName: process.env.DOCUMENTS_BUCKET_NAME || 'live2d-aws-backend-documentsbucket-gvqh2hzqj761',
      ragEnabled: process.env.RAG_ENABLED === 'false' ? false : true, // Default to enabled
    },
    live2d: {
      defaultModel: 'live2d-models/elaina/elaina.model3.json',
      scale: 0.005,
      initialXshift: 0,
      initialYshift: 0,
      emotionMap: {}
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
    httpBase: process.env.HTTP_BASE || process.env.VITE_HTTP_BASE || '',
    features: {
      useLocalTTS: defBool(process.env.FEATURE_USE_LOCAL_TTS || process.env.VITE_FEATURE_USE_LOCAL_TTS, true),
      useLocalSTT: defBool(process.env.FEATURE_USE_LOCAL_STT || process.env.VITE_FEATURE_USE_LOCAL_STT, true),
      useCloudFallbacks: defBool(process.env.FEATURE_USE_CLOUD_FALLBACKS || process.env.VITE_FEATURE_USE_CLOUD_FALLBACKS, true),
      useLocalWS: defBool(process.env.FEATURE_USE_LOCAL_WS || process.env.VITE_FEATURE_USE_LOCAL_WS, false),
    },
    aws: {
      region: process.env.AWS_REGION || process.env.VITE_AWS_REGION || 'us-west-2',
      wsUrl: process.env.WS_URL || process.env.VITE_WS_URL || 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
      httpBaseUrl: process.env.HTTP_BASE || process.env.VITE_HTTP_BASE || 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
      cognitoUserPoolId: process.env.COGNITO_USER_POOL_ID || process.env.VITE_COGNITO_USER_POOL_ID || '',
      cognitoClientId: process.env.COGNITO_CLIENT_ID || process.env.VITE_COGNITO_CLIENT_ID || '',
      cognitoDomain: process.env.COGNITO_DOMAIN || process.env.VITE_COGNITO_DOMAIN || '',
      modelId: process.env.MODEL_ID || process.env.VITE_MODEL_ID || 'anthropic.claude-3-7-sonnet-20250219-v1:0',
      // RAG Configuration
      documentsBucketName: process.env.DOCUMENTS_BUCKET_NAME || 'live2d-aws-backend-documentsbucket-gvqh2hzqj761',
      ragEnabled: process.env.RAG_ENABLED === 'false' ? false : true, // Default to enabled
    },
    live2d: {
      defaultModel: process.env.DEFAULT_MODEL || 'live2d-models/elaina/elaina.model3.json',
      scale: parseFloat(process.env.MODEL_SCALE || '0.05')
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
    },
    live2d: {
      ...(envConfig.live2d || {}),
      ...(storedConfig.live2d || {}),
    }
  };

  // Log the configuration on first read
  if (!global.configLogged) {
    logConfig(mergedConfig);
    global.configLogged = true;
  }

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
