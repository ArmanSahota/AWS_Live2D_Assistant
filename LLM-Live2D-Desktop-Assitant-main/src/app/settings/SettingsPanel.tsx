/**
 * Settings Panel Component
 * 
 * This component provides a UI for configuring the application settings.
 * It allows the user to toggle features and configure AWS settings.
 */

import React, { useState, useEffect } from 'react';
import { readConfig, saveConfig, getFeatureFlags, updateFeatureFlags, getAWSConfig, updateAWSConfig } from '../../config/appConfig';
import { isLoggedIn, logout } from '../../infra/auth/noneAuth';
import { connectWS } from '../../infra/ws/wsClient';
import { speak } from '../speech/ttsBridge';

// Add type declaration for window.electronAPI
declare global {
  interface Window {
    electronAPI: {
      login: () => Promise<void>;
    }
  }
}

// Define the component props
interface SettingsPanelProps {
  onClose: () => void;
}

// Define the settings panel component
const SettingsPanel: React.FC<SettingsPanelProps> = ({ onClose }) => {
  // State for feature flags
  const [useLocalTTS, setUseLocalTTS] = useState(true);
  const [useLocalSTT, setUseLocalSTT] = useState(true);
  const [useCloudFallbacks, setUseCloudFallbacks] = useState(true);
  
  // State for HTTP config
  const [httpBase, setHttpBase] = useState('');
  
  // State for AWS config
  const [region, setRegion] = useState('us-east-1');
  const [wsUrl, setWsUrl] = useState('');
  const [httpBaseUrl, setHttpBaseUrl] = useState('');
  const [cognitoUserPoolId, setCognitoUserPoolId] = useState('');
  const [cognitoClientId, setCognitoClientId] = useState('');
  const [cognitoDomain, setCognitoDomain] = useState('');
  
  // State for test results
  const [cloudTestResult, setCloudTestResult] = useState<string | null>(null);
  const [ttsTestResult, setTtsTestResult] = useState<string | null>(null);
  const [wsTestResult, setWsTestResult] = useState<string | null>(null);
  const [httpTestResult, setHttpTestResult] = useState<string | null>(null);
  
  // State for authentication
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Load settings on component mount
  useEffect(() => {
    loadSettings();
    checkAuthentication();
  }, []);
  
  // Load settings from the config
  const loadSettings = () => {
    // Load app config
    const config = readConfig();
    setHttpBase(config.httpBase);
    
    // Load feature flags
    const flags = getFeatureFlags();
    setUseLocalTTS(flags.useLocalTTS);
    setUseLocalSTT(flags.useLocalSTT);
    setUseCloudFallbacks(flags.useCloudFallbacks);
    
    // Load AWS config
    const awsConfig = getAWSConfig();
    setRegion(awsConfig.region);
    setWsUrl(awsConfig.wsUrl);
    setHttpBaseUrl(awsConfig.httpBaseUrl);
    setCognitoUserPoolId(awsConfig.cognitoUserPoolId);
    setCognitoClientId(awsConfig.cognitoClientId);
    setCognitoDomain(awsConfig.cognitoDomain);
  };
  
  // Check authentication status
  const checkAuthentication = () => {
    setIsAuthenticated(isLoggedIn());
  };
  
  // Save feature flags
  const saveFeatureFlags = () => {
    updateFeatureFlags({
      useLocalTTS,
      useLocalSTT,
      useCloudFallbacks
    });
  };
  
  // Save HTTP base URL
  const saveHttpBase = () => {
    saveConfig({
      httpBase
    });
  };
  
  // Save AWS config
  const saveAWSConfig = () => {
    updateAWSConfig({
      region,
      wsUrl,
      httpBaseUrl,
      cognitoUserPoolId,
      cognitoClientId,
      cognitoDomain
    });
  };
  
  // Handle login
  const handleLogin = async () => {
    try {
      // This will trigger the login flow in the main process
      await window.electronAPI.login();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  
  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };
  
  // Test cloud connection
  const testCloud = async () => {
    try {
      setCloudTestResult('Testing...');
      const result = await window.api.getHealth();
      setCloudTestResult(`Success! Status: ${result.status}, Latency: ${result.latency}ms`);
    } catch (error) {
      setCloudTestResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  
  // Test TTS
  const testTTS = async () => {
    try {
      setTtsTestResult('Testing...');
      const result = await speak('This is a test of the text-to-speech system.');
      setTtsTestResult(`Success! Source: ${result.source}`);
    } catch (error) {
      setTtsTestResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  
  // Test WebSocket
  const testWS = async () => {
    try {
      setWsTestResult('Testing...');
      
      // Create a WebSocket client
      const client = await connectWS(async () => {
        if (!isLoggedIn()) {
          throw new Error('Not authenticated');
        }
        return 'dummy-token'; // This is just for testing
      });
      
      // Set up message handler
      client.onMessage((message) => {
        if (message.type === 'server_event' && message.name === 'echo_response') {
          setWsTestResult(`Success! Received echo: ${JSON.stringify(message.data)}`);
        }
      });
      
      // Set up status handler
      client.onStatus((status) => {
        if (status === 'error') {
          setWsTestResult('Error: WebSocket connection failed');
        }
      });
      
      // Send an echo message
      client.send({
        action: 'heartbeat',
        timestamp: Date.now()
      });
      
      // Close the connection after 5 seconds
      setTimeout(() => {
        client.close();
      }, 5000);
    } catch (error) {
      setWsTestResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  
  return (
    <div className="settings-panel">
      <h2>Settings</h2>
      
      <div className="settings-section">
        <h3>Feature Flags</h3>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={useLocalTTS}
              onChange={(e) => setUseLocalTTS(e.target.checked)}
            />
            Use Local TTS
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={useLocalSTT}
              onChange={(e) => setUseLocalSTT(e.target.checked)}
            />
            Use Local STT
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={useCloudFallbacks}
              onChange={(e) => setUseCloudFallbacks(e.target.checked)}
            />
            Use Cloud Fallbacks
          </label>
        </div>
        
        <button onClick={saveFeatureFlags}>Save Feature Flags</button>
      </div>
      
      <div className="settings-section">
        <h3>HTTP Configuration</h3>
        
        <div className="setting-item">
          <label>
            HTTP Base URL:
            <input
              type="text"
              value={httpBase}
              onChange={(e) => setHttpBase(e.target.value)}
              placeholder="https://example.execute-api.us-west-2.amazonaws.com/dev"
            />
          </label>
          {!httpBase && (
            <p className="warning">HTTP Base URL is required for Claude HTTP API</p>
          )}
        </div>
        
        <button onClick={saveHttpBase}>Save HTTP Config</button>
      </div>
      
      <div className="settings-section">
        <h3>AWS Configuration</h3>
        
        <div className="setting-item">
          <label>
            Region:
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
            />
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            WebSocket URL:
            <input
              type="text"
              value={wsUrl}
              onChange={(e) => setWsUrl(e.target.value)}
            />
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            HTTP Base URL:
            <input
              type="text"
              value={httpBaseUrl}
              onChange={(e) => setHttpBaseUrl(e.target.value)}
            />
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            Cognito User Pool ID:
            <input
              type="text"
              value={cognitoUserPoolId}
              onChange={(e) => setCognitoUserPoolId(e.target.value)}
            />
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            Cognito Client ID:
            <input
              type="text"
              value={cognitoClientId}
              onChange={(e) => setCognitoClientId(e.target.value)}
            />
          </label>
        </div>
        
        <div className="setting-item">
          <label>
            Cognito Domain:
            <input
              type="text"
              value={cognitoDomain}
              onChange={(e) => setCognitoDomain(e.target.value)}
            />
          </label>
        </div>
        
        <button onClick={saveAWSConfig}>Save AWS Config</button>
      </div>
      
      <div className="settings-section">
        <h3>Authentication</h3>
        
        <div className="setting-item">
          <p>Status: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</p>
          
          {isAuthenticated ? (
            <button onClick={handleLogout}>Log Out</button>
          ) : (
            <button onClick={handleLogin}>Log In</button>
          )}
        </div>
      </div>
      
      <div className="settings-section">
        <h3>Tests</h3>
        
        <div className="setting-item">
          <button onClick={testCloud}>Test Cloud Health</button>
          {cloudTestResult && <p>{cloudTestResult}</p>}
        </div>
        
        <div className="setting-item">
          <button onClick={testTTS}>Test TTS</button>
          {ttsTestResult && <p>{ttsTestResult}</p>}
        </div>
        
        <div className="setting-item">
          <button onClick={testWS}>Test WebSocket</button>
          {wsTestResult && <p>{wsTestResult}</p>}
        </div>
      </div>
      
      <div className="settings-actions">
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default SettingsPanel;
