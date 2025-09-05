/**
 * Authentication Gate Component
 * 
 * This component handles the authentication flow.
 * It shows a sign-in button if the user is not authenticated,
 * and renders the children if the user is authenticated.
 */

import React, { useState, useEffect } from 'react';
import { isLoggedIn } from '../../infra/auth/cognitoAuth';

// Define the component props
interface AuthGateProps {
  children: React.ReactNode;
}

// Define the authentication gate component
const AuthGate: React.FC<AuthGateProps> = ({ children }) => {
  // State for authentication status
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Check authentication status on component mount
  useEffect(() => {
    checkAuthentication();
    
    // Register for auth callback
    window.electronAPI.handleAuthCallback((data) => {
      if (data.success) {
        setIsAuthenticated(true);
      }
    });
    
    // Set up interval to refresh authentication status
    const interval = setInterval(checkAuthentication, 5000);
    
    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, []);
  
  // Check authentication status
  const checkAuthentication = () => {
    setIsAuthenticated(isLoggedIn());
    setIsLoading(false);
  };
  
  // Handle login
  const handleLogin = async () => {
    try {
      setIsLoading(true);
      await window.electronAPI.login();
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
    }
  };
  
  // If loading, show loading indicator
  if (isLoading) {
    return (
      <div className="auth-gate loading">
        <p>Loading...</p>
      </div>
    );
  }
  
  // If not authenticated, show sign-in button
  if (!isAuthenticated) {
    return (
      <div className="auth-gate">
        <h2>Authentication Required</h2>
        <p>Please sign in to continue.</p>
        <button onClick={handleLogin}>Sign In</button>
      </div>
    );
  }
  
  // If authenticated, render children
  return <>{children}</>;
};

export default AuthGate;
