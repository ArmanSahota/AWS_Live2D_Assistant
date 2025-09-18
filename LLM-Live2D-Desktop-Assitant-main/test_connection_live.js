const WebSocket = require('ws');

// Test WebSocket connection to the backend
const serverPort = 1020;
const wsUrl = `ws://localhost:${serverPort}/client-ws`;

console.log(`Testing WebSocket connection to: ${wsUrl}`);

const ws = new WebSocket(wsUrl);

ws.on('open', function open() {
    console.log('✅ WebSocket connection established successfully!');
    console.log('Backend and frontend can communicate properly.');
    
    // Send a test message
    ws.send(JSON.stringify({
        type: 'test',
        message: 'Hello from frontend test!'
    }));
});

ws.on('message', function message(data) {
    console.log('📨 Received from backend:', data.toString());
});

ws.on('error', function error(err) {
    console.log('❌ WebSocket connection failed:', err.message);
    console.log('Backend and frontend cannot communicate.');
});

ws.on('close', function close() {
    console.log('🔌 WebSocket connection closed');
    process.exit(0);
});

// Close connection after 5 seconds
setTimeout(() => {
    console.log('Closing test connection...');
    ws.close();
}, 5000);