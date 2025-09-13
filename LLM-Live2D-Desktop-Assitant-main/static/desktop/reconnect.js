/**
 * Reconnection Script for Electron App
 * 
 * This script provides a function to reconnect the WebSocket connection
 * when it fails or disconnects unexpectedly.
 */

// Function to reconnect the WebSocket
function reconnectWebSocket() {
  console.log("Attempting to reconnect WebSocket...");
  
  // Check if window.ws exists and is not in OPEN state
  if (!window.ws || window.ws.readyState !== WebSocket.OPEN) {
    console.log("WebSocket is not open. Reconnecting...");
    
    // Check if WebSocket server is available
    if (!window.wsServerAvailable) {
      console.log("WebSocket server marked as unavailable. Skipping reconnection.");
      return;
    }
    
    // Try to connect
    window.connectWebSocket().then(() => {
      console.log("WebSocket reconnected successfully");
      
      // Fetch configurations after reconnection
      setTimeout(() => {
        window.fetchConfigurations();
        console.log("Fetched configurations after reconnection");
      }, 1000);
    }).catch(error => {
      // The connectWebSocket function now handles reconnection attempts internally
      // and will update the wsServerAvailable flag if needed
      console.log("Failed to reconnect WebSocket");
    });
  }
}

// Add a periodic check for WebSocket connection
function setupReconnectionCheck() {
  // Check every 10 seconds if the WebSocket is connected, but only for a limited time
  let checkCount = 0;
  const MAX_CHECKS = 6; // 6 checks at 10 seconds each = 1 minute total
  
  const intervalId = setInterval(() => {
    checkCount++;
    
    // Stop checking after MAX_CHECKS or if server is marked as unavailable
    if (checkCount >= MAX_CHECKS || (typeof window.wsServerAvailable !== 'undefined' && !window.wsServerAvailable)) {
      console.log(`Stopping WebSocket reconnection checks after ${checkCount} attempts`);
      clearInterval(intervalId);
      return;
    }
    
    if (!window.ws || window.ws.readyState !== WebSocket.OPEN) {
      // Only log the first few attempts to reduce console spam
      if (checkCount <= 3) {
        console.log("WebSocket is not connected. Current state:", 
                   window.ws ? ["CONNECTING", "OPEN", "CLOSING", "CLOSED"][window.ws.readyState] : "undefined");
      }
      reconnectWebSocket();
    }
  }, 10000);
}

// Export the functions
window.reconnectWebSocket = reconnectWebSocket;
window.setupReconnectionCheck = setupReconnectionCheck;

// Setup the reconnection check when the script loads
document.addEventListener('DOMContentLoaded', () => {
  console.log("Setting up WebSocket reconnection check");
  setupReconnectionCheck();
});
