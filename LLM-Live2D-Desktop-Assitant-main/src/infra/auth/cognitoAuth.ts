/**
 * Cognito Authentication Module
 * 
 * This module provides authentication functionality using Amazon Cognito.
 * It handles the authentication flow and token management.
 */

import { CognitoUserPool, CognitoUser, AuthenticationDetails, CognitoUserSession, CognitoRefreshToken } from 'amazon-cognito-identity-js';
import { getAWSConfig } from '../../config/appConfig';

// Token storage
let idToken: string | null = null;
let refreshToken: string | null = null;
let tokenExpiration: number | null = null;

/**
 * Initialize the Cognito User Pool
 * @returns The Cognito User Pool instance
 */
function getUserPool() {
  const config = getAWSConfig();
  return new CognitoUserPool({
    UserPoolId: config.cognitoUserPoolId,
    ClientId: config.cognitoClientId,
  });
}

/**
 * Store the authentication tokens securely
 * @param session The Cognito User Session containing the tokens
 */
export function storeTokens(session: CognitoUserSession): void {
  idToken = session.getIdToken().getJwtToken();
  refreshToken = session.getRefreshToken().getToken();
  tokenExpiration = session.getIdToken().getExpiration() * 1000; // Convert to milliseconds
}

/**
 * Store the ID token directly (used with hosted UI flow)
 * @param token The ID token to store
 */
export function storeIdToken(token: string): void {
  idToken = token;
  // Parse the token to get the expiration
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    tokenExpiration = payload.exp * 1000; // Convert to milliseconds
  } catch (error) {
    console.error('Error parsing token:', error);
    tokenExpiration = Date.now() + 3600000; // Default to 1 hour
  }
}

/**
 * Check if the user is logged in
 * @returns True if the user is logged in and the token is valid
 */
export function isLoggedIn(): boolean {
  if (!idToken || !tokenExpiration) {
    return false;
  }
  
  // Check if the token is expired
  return Date.now() < tokenExpiration;
}

/**
 * Get the current ID token
 * @returns The ID token if available and valid, null otherwise
 */
export async function getIdToken(): Promise<string | null> {
  if (!isLoggedIn()) {
    // Try to refresh the token if we have a refresh token
    if (refreshToken) {
      try {
        await refreshSession();
      } catch (error) {
        console.error('Error refreshing token:', error);
        return null;
      }
    } else {
      return null;
    }
  }
  
  return idToken;
}

/**
 * Refresh the authentication session
 * @returns A promise that resolves when the session is refreshed
 */
export async function refreshSession(): Promise<void> {
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  return new Promise<void>((resolve, reject) => {
    const userPool = getUserPool();
    const cognitoUser = userPool.getCurrentUser();
    
    if (!cognitoUser) {
      reject(new Error('No user found'));
      return;
    }
    
    // Create a CognitoRefreshToken object
    // We've already checked that refreshToken is not null above
    const cognitoRefreshToken = new CognitoRefreshToken({ RefreshToken: refreshToken as string });
    
    cognitoUser.refreshSession(cognitoRefreshToken, (err: Error | null, session: CognitoUserSession | null) => {
      if (err) {
        reject(err);
        return;
      }
      
      if (!session) {
        reject(new Error('No session returned'));
        return;
      }
      
      storeTokens(session);
      resolve();
    });
  });
}

/**
 * Log out the current user
 */
export function logout(): void {
  idToken = null;
  refreshToken = null;
  tokenExpiration = null;
  
  const userPool = getUserPool();
  const cognitoUser = userPool.getCurrentUser();
  
  if (cognitoUser) {
    cognitoUser.signOut();
  }
}

/**
 * Get the authentication headers for API requests
 * @returns The headers object with the Authorization header
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  const token = await getIdToken();
  
  if (!token) {
    return {};
  }
  
  return {
    Authorization: `Bearer ${token}`,
  };
}
