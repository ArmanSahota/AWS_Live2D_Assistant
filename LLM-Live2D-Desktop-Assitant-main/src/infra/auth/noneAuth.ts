/**
 * No Authentication Module
 * 
 * This module provides a stub for authentication functionality.
 * It will be replaced with Cognito authentication in the future.
 */

// Authentication state
let isAuthenticated = true; // Always authenticated in stub mode

/**
 * Check if the user is logged in
 * @returns Always true in stub mode
 */
export function isLoggedIn(): boolean {
  return isAuthenticated;
}

/**
 * Get the current ID token
 * @returns Empty string in stub mode
 */
export async function getIdToken(): Promise<string> {
  return "";
}

/**
 * Get the authentication headers for API requests
 * @returns Empty object in stub mode
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  return {};
}

/**
 * Log out the current user
 * Does nothing in stub mode
 */
export function logout(): void {
  // No-op in stub mode
}
