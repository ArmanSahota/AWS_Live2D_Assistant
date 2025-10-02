#!/usr/bin/env node

/**
 * Connection Test Script
 * Tests the WebSocket connection between frontend and backend
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

console.log('🔧 Testing Frontend-Backend Connection...\n');

// Test 1: Check if server_port.txt exists
console.log('📁 Test 1: Checking server_port.txt file...');
const portFilePath = path.join(__dirname, 'server_port.txt');

if (fs.existsSync(portFilePath)) {
    const portContent = fs.readFileSync(portFilePath, 'utf8').trim();
    const serverPort = parseInt(portContent);
    
    if (!isNaN(serverPort)) {
        console.log(`✅ Found server port: ${serverPort}`);
        
        // Test 2: Test HTTP health endpoint
        console.log('\n🏥 Test 2: Testing HTTP health endpoint...');
        testHealthEndpoint(serverPort);
        
        // Test 3: Test WebSocket connection
        console.log('\n🔌 Test 3: Testing WebSocket connection...');
        testWebSocketConnection(serverPort);
    } else {
        console.log('❌ Invalid port in server_port.txt:', portContent);
    }
} else {
    console.log('❌ server_port.txt not found. Server may not be running.');
    console.log('💡 Start the server with: python server.py');
}

async function testHealthEndpoint(port) {
    try {
        const response = await fetch(`http://localhost:${port}/health`);
        if (response.ok) {
            const data = await response.text();
            console.log(`✅ Health endpoint responded: ${data}`);
        } else {
            console.log(`❌ Health endpoint failed with status: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Health endpoint error: ${error.message}`);
    }
}

function testWebSocketConnection(port) {
    const wsUrl = `ws://localhost:${port}/client-ws`;
    console.log(`Connecting to: ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    
    ws.on('open', () => {
        console.log('✅ WebSocket connected successfully!');
        
        // Send a test message
        const testMessage = {
            type: 'test',
            message: 'Connection test from test script'
        };
        
        ws.send(JSON.stringify(testMessage));
        console.log('📤 Sent test message');
        
        // Close after a short delay
        setTimeout(() => {
            ws.close();
        }, 2000);
    });
    
    ws.on('message', (data) => {
        console.log('📥 Received message:', data.toString());
    });
    
    ws.on('close', (code, reason) => {
        console.log(`🔌 WebSocket closed. Code: ${code}, Reason: ${reason || 'Normal closure'}`);
    });
    
    ws.on('error', (error) => {
        console.log('❌ WebSocket error:', error.message);
    });
}

// Test 4: Check for critical files
console.log('\n📋 Test 4: Checking critical files...');

const criticalFiles = [
    'src/main/ipc.js',
    'src/main/models.js',
    'static/desktop/websocket.js',
    'static/desktop/live2d.js',
    'static/desktop.html'
];

criticalFiles.forEach(file => {
    const filePath = path.join(__dirname, file);
    if (fs.existsSync(filePath)) {
        console.log(`✅ ${file}`);
    } else {
        console.log(`❌ ${file} - MISSING`);
    }
});

// Test 5: Check wake word files
console.log('\n🎤 Test 5: Checking wake word files...');

const wakeWordFiles = [
    'static/desktop/Elaina_en_wasm_v3_0_0.ppn',
    'static/desktop/伊蕾娜_zh_wasm_v3_0_0.ppn',
    'static/desktop/Elaina_en_wasm_v3_0_0.js'
];

wakeWordFiles.forEach(file => {
    const filePath = path.join(__dirname, file);
    if (fs.existsSync(filePath)) {
        console.log(`✅ ${file}`);
    } else {
        console.log(`⚠️  ${file} - Missing (wake word may not work)`);
    }
});

console.log('\n🏁 Connection test completed!');
console.log('\n💡 If tests fail:');
console.log('   1. Make sure Python server is running: python server.py');
console.log('   2. Check for error messages in server console');
console.log('   3. Verify no firewall is blocking the ports');
console.log('   4. Try restarting both server and frontend');