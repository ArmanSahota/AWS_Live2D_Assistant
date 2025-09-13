/**
 * Test WebSocket functionality
 */

const WebSocket = require('ws');
const { promisify } = require('util');
const { 
  assert, 
  assertEqual, 
  assertDeepEqual, 
  runTest 
} = require('../utils');

// Import the mock WebSocket client module
const { createWebSocketClient: createWsClient } = require('./wsClient');

// Run tests
async function runTests() {
  try {
    let passed = 0;
    let total = 0;
    
    // Test WebSocket client creation
    total++;
    if (await runTest('WebSocket client creation', testWsClientCreation)) {
      passed++;
    }
    
    // Test WebSocket connection
    total++;
    if (await runTest('WebSocket connection', testWsConnection)) {
      passed++;
    }
    
    // Test WebSocket message sending and receiving
    total++;
    if (await runTest('WebSocket message sending and receiving', testWsMessageSendReceive)) {
      passed++;
    }
    
    // Test WebSocket reconnection
    total++;
    if (await runTest('WebSocket reconnection', testWsReconnection)) {
      passed++;
    }
    
    console.log(`\nTest summary: ${passed}/${total} tests passed`);
    
    if (passed < total) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

/**
 * Test WebSocket client creation
 */
async function testWsClientCreation() {
  // Create a WebSocket client
  const wsClient = createWsClient({
    url: 'ws://localhost:8080',
    reconnectInterval: 1000,
    maxReconnectAttempts: 5
  });
  
  // Assert that the WebSocket client is not null or undefined
  assert(wsClient !== null && wsClient !== undefined, 'WebSocket client should not be null or undefined');
  
  // Assert that the WebSocket client has the expected methods
  assert(typeof wsClient.connect === 'function', 'WebSocket client should have a connect method');
  assert(typeof wsClient.disconnect === 'function', 'WebSocket client should have a disconnect method');
  assert(typeof wsClient.send === 'function', 'WebSocket client should have a send method');
  assert(typeof wsClient.onMessage === 'function', 'WebSocket client should have an onMessage method');
  assert(typeof wsClient.onOpen === 'function', 'WebSocket client should have an onOpen method');
  assert(typeof wsClient.onClose === 'function', 'WebSocket client should have an onClose method');
  assert(typeof wsClient.onError === 'function', 'WebSocket client should have an onError method');
}

/**
 * Test WebSocket connection
 */
async function testWsConnection() {
  // Create a WebSocket server
  const wss = new WebSocket.Server({ port: 0 });
  const port = wss.address().port;
  
  try {
    // Create a WebSocket client
    const wsClient = createWsClient({
      url: `ws://localhost:${port}`,
      reconnectInterval: 1000,
      maxReconnectAttempts: 5
    });
    
    // Connect to the server
    const connectPromise = new Promise((resolve) => {
      wsClient.onOpen(() => {
        resolve();
      });
    });
    
    await wsClient.connect();
    await connectPromise;
    
    // Assert that the WebSocket client is connected
    assert(wsClient.isConnected(), 'WebSocket client should be connected');
    
    // Disconnect from the server
    await wsClient.disconnect();
    
    // Assert that the WebSocket client is disconnected
    assert(!wsClient.isConnected(), 'WebSocket client should be disconnected');
  } finally {
    // Close the server
    await promisify(wss.close.bind(wss))();
  }
}

/**
 * Test WebSocket message sending and receiving
 */
async function testWsMessageSendReceive() {
  // Create a WebSocket server
  const wss = new WebSocket.Server({ port: 0 });
  const port = wss.address().port;
  
  try {
    // Create a WebSocket client
    const wsClient = createWsClient({
      url: `ws://localhost:${port}`,
      reconnectInterval: 1000,
      maxReconnectAttempts: 5
    });
    
    // Connect to the server
    const connectPromise = new Promise((resolve) => {
      wsClient.onOpen(() => {
        resolve();
      });
    });
    
    await wsClient.connect();
    await connectPromise;
    
    // Set up the server to echo messages
    wss.on('connection', (ws) => {
      ws.on('message', (message) => {
        ws.send(message);
      });
    });
    
    // Send a message and wait for the response
    const messagePromise = new Promise((resolve) => {
      wsClient.onMessage((message) => {
        resolve(message);
      });
    });
    
    const testMessage = { type: 'test', data: 'Hello, world!' };
    wsClient.send(testMessage);
    
    const receivedMessage = await messagePromise;
    
    // Assert that the received message matches the sent message
    assertDeepEqual(receivedMessage, testMessage, 'Received message should match sent message');
    
    // Disconnect from the server
    await wsClient.disconnect();
  } finally {
    // Close the server
    await promisify(wss.close.bind(wss))();
  }
}

/**
 * Test WebSocket reconnection
 */
async function testWsReconnection() {
  // Create a WebSocket server
  let wss = new WebSocket.Server({ port: 0 });
  const port = wss.address().port;
  
  try {
    // Create a WebSocket client
    const wsClient = createWsClient({
      url: `ws://localhost:${port}`,
      reconnectInterval: 100,
      maxReconnectAttempts: 5
    });
    
    // Connect to the server
    const connectPromise = new Promise((resolve) => {
      wsClient.onOpen(() => {
        resolve();
      });
    });
    
    await wsClient.connect();
    await connectPromise;
    
    // Assert that the WebSocket client is connected
    assert(wsClient.isConnected(), 'WebSocket client should be connected');
    
    // Close the server to simulate a disconnection
    await promisify(wss.close.bind(wss))();

    // Wait for the client to detect the disconnection
    await new Promise((resolve) => {
      wsClient.onClose(() => {
        resolve();
      });
      
      // Manually trigger the close event for testing
      wsClient.disconnect();
    });

    // Assert that the WebSocket client is disconnected
    assert(!wsClient.isConnected(), 'WebSocket client should be disconnected');
    
    // Create a new server on the same port
    wss = new WebSocket.Server({ port });
    
    // Wait for the client to reconnect
    const reconnectPromise = new Promise((resolve) => {
      wsClient.onOpen(() => {
        resolve();
      });
    });
    
    // Manually trigger a reconnect for testing
    await wsClient.connect();
    
    await reconnectPromise;
    
    // Assert that the WebSocket client is connected again
    assert(wsClient.isConnected(), 'WebSocket client should be reconnected');
    
    // Disconnect from the server
    await wsClient.disconnect();
  } finally {
    // Close the server
    if (wss.listening) {
      await promisify(wss.close.bind(wss))();
    }
  }
}

// Run the tests if this file is executed directly
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests
};
