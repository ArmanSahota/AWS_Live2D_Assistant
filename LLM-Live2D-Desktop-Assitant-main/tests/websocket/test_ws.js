const WebSocket = require('ws');

// Create a WebSocket connection
const ws = new WebSocket('wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev');

// Connection opened
ws.on('open', function() {
  console.log('Connected to WebSocket server');
  
  // Send a test message
  const message = {
    action: 'chat',
    text: 'Hello, WebSocket!',
    sessionId: `session-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`
  };
  
  console.log('Sending message:', JSON.stringify(message));
  ws.send(JSON.stringify(message));
});

// Listen for messages
ws.on('message', function(data) {
  console.log('Received message:', data.toString());
});

// Handle errors
ws.on('error', function(error) {
  console.error('WebSocket error:', error);
});

// Connection closed
ws.on('close', function() {
  console.log('Connection closed');
});

// Close the connection after 5 seconds
setTimeout(() => {
  ws.close();
  console.log('Test completed');
}, 5000);
