/**
 * WebSocket reconnection utility for testing
 * 
 * This module provides a utility function for reconnecting to a WebSocket server.
 */

const WebSocket = require('ws');
const EventEmitter = require('events');

// Create an event emitter to simulate WebSocket events
const eventEmitter = new EventEmitter();

// Track connection state
let ws = null;
let isConnected = false;
let reconnectAttempts = 0;
let reconnectInterval = null;

/**
 * Reconnect to the WebSocket server
 * @param {string} url - WebSocket server URL
 * @param {Object} options - Reconnection options
 * @param {number} options.maxAttempts - Maximum number of reconnection attempts
 * @param {number} options.delay - Delay between reconnection attempts in milliseconds
 * @returns {Promise<WebSocket>} - WebSocket connection
 */
async function reconnectWebSocket(url, options = {}) {
  const maxAttempts = options.maxAttempts || 5;
  const delay = options.delay || 1000;
  
  // Clear existing reconnect interval if it exists
  if (reconnectInterval) {
    clearInterval(reconnectInterval);
    reconnectInterval = null;
  }
  
  // Reset reconnect attempts
  reconnectAttempts = 0;
  
  // Close existing connection if it exists
  if (ws) {
    ws.close();
    ws = null;
  }
  
  // Create a new WebSocket connection
  return new Promise((resolve, reject) => {
    function attemptConnect() {
      try {
        console.log(`Attempting to connect to ${url}...`);
        
        // Create a new WebSocket connection
        ws = new WebSocket(url);
        
        // Set up event handlers
        ws.on('open', () => {
          console.log('WebSocket connection established');
          isConnected = true;
          reconnectAttempts = 0;
          eventEmitter.emit('open');
          resolve(ws);
        });
        
        ws.on('close', () => {
          console.log('WebSocket connection closed');
          isConnected = false;
          eventEmitter.emit('close');
          
          // Attempt to reconnect if not manually closed
          if (reconnectInterval) {
            reconnectAttempts++;
            
            if (reconnectAttempts < maxAttempts) {
              console.log(`Reconnection attempt ${reconnectAttempts}/${maxAttempts}`);
              eventEmitter.emit('reconnect', { attempt: reconnectAttempts });
            } else {
              console.log('Maximum reconnection attempts reached');
              clearInterval(reconnectInterval);
              reconnectInterval = null;
              eventEmitter.emit('reconnect:failed');
              reject(new Error('Maximum reconnection attempts reached'));
            }
          }
        });
        
        ws.on('error', (error) => {
          console.error('WebSocket error:', error);
          eventEmitter.emit('error', error);
        });
      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        reject(error);
      }
    }
    
    // Attempt to connect immediately
    attemptConnect();
    
    // Set up reconnect interval
    reconnectInterval = setInterval(() => {
      if (!isConnected && reconnectAttempts < maxAttempts) {
        attemptConnect();
      } else if (reconnectAttempts >= maxAttempts) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
      }
    }, delay);
  });
}

/**
 * Test the reconnection functionality
 */
async function testReconnect() {
  try {
    // Create a WebSocket server
    const wss = new WebSocket.Server({ port: 0 });
    const port = wss.address().port;
    const url = `ws://localhost:${port}`;
    
    console.log(`WebSocket server started on ${url}`);
    
    // Set up the server to handle connections
    wss.on('connection', (ws) => {
      console.log('Client connected to server');
      
      ws.on('message', (message) => {
        console.log(`Received message: ${message}`);
        ws.send(message);
      });
    });
    
    // Connect to the server
    const client = await reconnectWebSocket(url, {
      maxAttempts: 5,
      delay: 1000
    });
    
    console.log('Connected to WebSocket server');
    
    // Send a test message
    client.send('Hello, WebSocket!');
    
    // Wait for a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Close the server to simulate a disconnection
    wss.close();
    
    console.log('Server closed, simulating disconnection');
    
    // Wait for a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create a new server on the same port
    const newWss = new WebSocket.Server({ port });
    
    console.log('New server started on the same port');
    
    // Wait for the client to reconnect
    await new Promise(resolve => {
      eventEmitter.once('open', () => {
        console.log('Client reconnected to server');
        resolve();
      });
    });
    
    // Send another test message
    client.send('Hello again, WebSocket!');
    
    // Wait for a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Close the client and server
    client.close();
    newWss.close();
    
    console.log('Test completed successfully');
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Export the reconnect function
module.exports = {
  reconnectWebSocket,
  testReconnect
};

// Run the test if this file is executed directly
if (require.main === module) {
  testReconnect();
}
