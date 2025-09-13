/**
 * Mock WebSocket client for testing
 */

const EventEmitter = require('events');

/**
 * Create a WebSocket client
 * @param {Object} options - WebSocket client options
 * @param {string} options.url - WebSocket server URL
 * @param {Object} options.auth - Authentication options
 * @returns {Object} - WebSocket client
 */
function createWebSocketClient(options = {}) {
  const url = options.url || 'ws://localhost:8080';
  const auth = options.auth || {};
  
  // Create an event emitter to simulate WebSocket events
  const eventEmitter = new EventEmitter();
  
  // Simulate connection state
  let isConnected = false;
  let reconnectAttempts = 0;
  let reconnectInterval = null;
  
  return {
    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    connect: async () => {
      // Simulate connection delay
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Simulate successful connection
      isConnected = true;
      eventEmitter.emit('open');
      
      return Promise.resolve();
    },
    
    /**
     * Register an open event handler
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    onOpen: (handler) => {
      eventEmitter.on('open', handler);
    },
    
    /**
     * Register a close event handler
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    onClose: (handler) => {
      eventEmitter.on('close', handler);
    },
    
    /**
     * Register a message event handler
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    onMessage: (handler) => {
      eventEmitter.on('message', handler);
    },
    
    /**
     * Register an error event handler
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    onError: (handler) => {
      eventEmitter.on('error', handler);
    },
    
    /**
     * Disconnect from the WebSocket server
     * @returns {Promise<void>}
     */
    disconnect: async () => {
      // Simulate disconnection
      isConnected = false;
      eventEmitter.emit('close');
      
      // Clear reconnect interval if it exists
      if (reconnectInterval) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
      }
      
      return Promise.resolve();
    },
    
    /**
     * Send a message to the WebSocket server
     * @param {Object} message - Message to send
     * @returns {Promise<void>}
     */
    send: async (message) => {
      // Check if connected
      if (!isConnected) {
        throw new Error('WebSocket is not connected');
      }
      
      // Simulate sending a message
      eventEmitter.emit('message:sent', message);
      
      // Simulate receiving a response - echo back the same message
      setTimeout(() => {
        eventEmitter.emit('message', message);
      }, 10);
      
      return Promise.resolve();
    },
    
    /**
     * Check if the WebSocket is connected
     * @returns {boolean}
     */
    isConnected: () => {
      return isConnected;
    },
    
    /**
     * Enable automatic reconnection
     * @param {Object} options - Reconnection options
     * @param {number} options.maxAttempts - Maximum number of reconnection attempts
     * @param {number} options.delay - Delay between reconnection attempts in milliseconds
     * @returns {void}
     */
    enableReconnect: (options = {}) => {
      const maxAttempts = options.maxAttempts || 5;
      const delay = options.delay || 1000;
      
      // Clear existing reconnect interval if it exists
      if (reconnectInterval) {
        clearInterval(reconnectInterval);
      }
      
      // Set up reconnect interval
      reconnectInterval = setInterval(async () => {
        if (!isConnected && reconnectAttempts < maxAttempts) {
          reconnectAttempts++;
          eventEmitter.emit('reconnect', { attempt: reconnectAttempts });
          
          try {
            await this.connect();
            reconnectAttempts = 0;
          } catch (error) {
            eventEmitter.emit('error', error);
          }
        } else if (reconnectAttempts >= maxAttempts) {
          clearInterval(reconnectInterval);
          reconnectInterval = null;
          eventEmitter.emit('reconnect:failed');
        }
      }, delay);
    },
    
    /**
     * Disable automatic reconnection
     * @returns {void}
     */
    disableReconnect: () => {
      if (reconnectInterval) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
      }
    },
    
    /**
     * Register an event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    on: (event, handler) => {
      eventEmitter.on(event, handler);
    },
    
    /**
     * Remove an event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    off: (event, handler) => {
      eventEmitter.off(event, handler);
    },
    
    /**
     * Register a one-time event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @returns {void}
     */
    once: (event, handler) => {
      eventEmitter.once(event, handler);
    }
  };
}

module.exports = {
  createWebSocketClient
};
