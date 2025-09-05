/**
 * Status Bar Component
 * 
 * This component displays the status of various system components.
 * It shows the connection status, authentication status, and feature flags.
 */

import React, { useState, useEffect } from 'react';
import { getFeatureFlags } from '../../config/appConfig';
import { isLoggedIn } from '../../infra/auth/noneAuth';
import { onStatus } from '../chat/pipe';

// Define the component props
interface StatusBarProps {
  onSettingsClick: () => void;
}

// Define the status bar component
const StatusBar: React.FC<StatusBarProps> = ({ onSettingsClick }) => {
  // State for connection status
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  // State for authentication status
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // State for feature flags
  const [useLocalTTS, setUseLocalTTS] = useState(true);
  const [useLocalSTT, setUseLocalSTT] = useState(true);
  
  // State for cloud health
  const [cloudHealth, setCloudHealth] = useState<'ok' | 'error' | 'unknown'>('unknown');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  
  // Load status on component mount
  useEffect(() => {
    // Load feature flags
    const flags = getFeatureFlags();
    setUseLocalTTS(flags.useLocalTTS);
    setUseLocalSTT(flags.useLocalSTT);
    
    // Check authentication status
    setIsAuthenticated(isLoggedIn());
    
    // Register for connection status updates
    onStatus(setConnectionStatus);
    
    // Check cloud health
    checkCloudHealth();
    
    // Set up interval to refresh status
    const interval = setInterval(() => {
      const flags = getFeatureFlags();
      setUseLocalTTS(flags.useLocalTTS);
      setUseLocalSTT(flags.useLocalSTT);
      setIsAuthenticated(isLoggedIn());
      checkCloudHealth();
    }, 60000); // Check every minute
    
    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, []);
  
  // Check cloud health
  const checkCloudHealth = async () => {
    try {
      const result = await window.api.getHealth();
      setCloudHealth(result.status === 'ok' ? 'ok' : 'error');
      setLastChecked(new Date());
    } catch (error) {
      console.error('Health check failed:', error);
      setCloudHealth('error');
      setLastChecked(new Date());
    }
  };
  
  // Get the connection status icon
  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'disconnected':
        return '⚪';
      case 'error':
        return '🔴';
    }
  };
  
  // Get the authentication status icon
  const getAuthIcon = () => {
    return isAuthenticated ? '🔒' : '🔓';
  };
  
  // Get the TTS status icon
  const getTTSIcon = () => {
    return useLocalTTS ? '🔊' : '🔇';
  };
  
  // Get the STT status icon
  const getSTTIcon = () => {
    return useLocalSTT ? '🎤' : '🚫';
  };
  
  // Get the cloud health icon
  const getCloudHealthIcon = () => {
    switch (cloudHealth) {
      case 'ok':
        return '✅';
      case 'error':
        return '❌';
      case 'unknown':
      default:
        return '❓';
    }
  };
  
  // Format the last checked time
  const formatLastChecked = () => {
    if (!lastChecked) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - lastChecked.getTime();
    
    if (diff < 60000) {
      return 'Just now';
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}m ago`;
    } else {
      return `${Math.floor(diff / 3600000)}h ago`;
    }
  };
  
  return (
    <div className="status-bar">
      <div className="status-item" title="Connection Status">
        {getConnectionIcon()} {connectionStatus}
      </div>
      <div className="status-item" title="Cloud Health">
        {getCloudHealthIcon()} Cloud {cloudHealth} (checked {formatLastChecked()})
      </div>
      <div className="status-item" title="Local TTS Status">
        {getTTSIcon()} Local TTS {useLocalTTS ? 'Enabled' : 'Disabled'}
      </div>
      <div className="status-item" title="Local STT Status">
        {getSTTIcon()} Local STT {useLocalSTT ? 'Enabled' : 'Disabled'}
      </div>
      <div className="status-item">
        <button onClick={onSettingsClick}>Settings</button>
      </div>
    </div>
  );
};

export default StatusBar;
