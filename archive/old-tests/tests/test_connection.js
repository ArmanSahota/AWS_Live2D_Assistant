/**
 * Test WebSocket Connection - Find working port
 * Usage: node test_connection.js
 */
const WebSocket = require('ws');

// Try different ports
const ports = [1018, 1019, 1020, 1025, 8000, 8080];

async function testPort(port) {
    return new Promise((resolve) => {
        console.log(`Testing port ${port}...`);
        const ws = new WebSocket(`ws://127.0.0.1:${port}/client-ws`);
        
        const timeout = setTimeout(() => {
            ws.terminate();
            resolve(false);
        }, 2000);
        
        ws.on('open', () => {
            console.log(`✅ Port ${port} - Connected successfully!`);
            clearTimeout(timeout);
            
            // Send test message
            ws.send(JSON.stringify({
                type: 'test',
                message: 'Hello from test client'
            }));
            
            ws.close();
            resolve(true);
        });
        
        ws.on('error', (err) => {
            console.log(`❌ Port ${port} - ${err.code || err.message}`);
            clearTimeout(timeout);
            resolve(false);
        });
    });
}

async function findWorkingPort() {
    console.log('=' .repeat(50));
    console.log('WEBSOCKET CONNECTION TEST');
    console.log('=' .repeat(50));
    console.log();
    
    for (const port of ports) {
        if (await testPort(port)) {
            console.log();
            console.log('=' .repeat(50));
            console.log(`✅ WEBSOCKET SERVER FOUND ON PORT ${port}`);
            console.log('=' .repeat(50));
            console.log();
            console.log('Update your config to use this port:');
            console.log(`  WebSocket URL: ws://127.0.0.1:${port}/client-ws`);
            return port;
        }
    }
    
    console.log();
    console.log('=' .repeat(50));
    console.log('❌ NO WEBSOCKET SERVER FOUND');
    console.log('=' .repeat(50));
    console.log();
    console.log('Troubleshooting:');
    console.log('1. Start the Python server: python server.py');
    console.log('2. Check if any firewall is blocking the ports');
    console.log('3. Try running as administrator');
    return null;
}

// Run test
findWorkingPort().then(port => {
    if (port) {
        console.log('\nNext steps:');
        console.log('1. Ensure Python server is running on this port');
        console.log('2. Update websocket.js to use this port');
        console.log('3. Start the Electron app: npm start');
    } else {
        console.log('\nPlease start the Python server first:');
        console.log('  python server.py');
    }
    process.exit(0);
}).catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
});