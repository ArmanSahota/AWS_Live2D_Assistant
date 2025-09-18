/**
 * Connection Diagnostic Tool
 * 
 * This script checks for backend servers running on various ports
 * and helps diagnose connection issues between frontend and backend.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const POSSIBLE_PORTS = [1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030];
const SERVER_PORT_FILE = path.join(__dirname, 'LLM-Live2D-Desktop-Assitant-main', 'server_port.txt');
const TIMEOUT = 1000; // 1 second timeout for each request

// ANSI color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
    bgRed: '\x1b[41m',
    bgGreen: '\x1b[42m',
    bgYellow: '\x1b[43m',
    bgBlue: '\x1b[44m'
};

// Print header
console.log(`${colors.bright}${colors.cyan}====================================${colors.reset}`);
console.log(`${colors.bright}${colors.cyan}  FRONTEND-BACKEND CONNECTION TEST  ${colors.reset}`);
console.log(`${colors.bright}${colors.cyan}====================================${colors.reset}`);
console.log();

// Check if server_port.txt exists
let filePort = null;
try {
    if (fs.existsSync(SERVER_PORT_FILE)) {
        filePort = parseInt(fs.readFileSync(SERVER_PORT_FILE, 'utf8').trim());
        console.log(`${colors.green}✓ Found server_port.txt file with port: ${filePort}${colors.reset}`);
    } else {
        console.log(`${colors.yellow}⚠ No server_port.txt file found${colors.reset}`);
    }
} catch (error) {
    console.log(`${colors.red}✗ Error reading server_port.txt: ${error.message}${colors.reset}`);
}

console.log();
console.log(`${colors.bright}Scanning ports ${POSSIBLE_PORTS[0]}-${POSSIBLE_PORTS[POSSIBLE_PORTS.length-1]} for active backend servers...${colors.reset}`);
console.log();

// Check each port
let activeServers = 0;
let promises = POSSIBLE_PORTS.map(port => {
    return new Promise(resolve => {
        const req = http.get({
            hostname: 'localhost',
            port: port,
            path: '/health',
            timeout: TIMEOUT
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    activeServers++;
                    let status = '';
                    try {
                        const parsed = JSON.parse(data);
                        status = parsed.status || '';
                    } catch (e) {
                        // Ignore parsing errors
                    }
                    
                    let portHighlight = '';
                    if (filePort === port) {
                        portHighlight = `${colors.bgGreen}${colors.bright} MATCHES server_port.txt ${colors.reset}`;
                    }
                    
                    console.log(`${colors.green}✓ Port ${port}: ACTIVE${colors.reset} ${status ? `(Status: ${status})` : ''} ${portHighlight}`);
                    resolve(true);
                } else {
                    console.log(`${colors.yellow}⚠ Port ${port}: Responded with status ${res.statusCode}${colors.reset}`);
                    resolve(false);
                }
            });
        });
        
        req.on('error', () => {
            console.log(`${colors.red}✗ Port ${port}: No server detected${colors.reset}`);
            resolve(false);
        });
        
        req.on('timeout', () => {
            console.log(`${colors.red}✗ Port ${port}: Connection timed out${colors.reset}`);
            req.destroy();
            resolve(false);
        });
    });
});

// Wait for all port checks to complete
Promise.all(promises).then(() => {
    console.log();
    if (activeServers === 0) {
        console.log(`${colors.bgRed}${colors.bright} NO ACTIVE SERVERS FOUND! ${colors.reset}`);
        console.log();
        console.log(`${colors.yellow}Possible issues:${colors.reset}`);
        console.log(`1. Backend server is not running`);
        console.log(`2. Backend server is running on a different port range`);
        console.log(`3. Firewall is blocking connections`);
        console.log();
        console.log(`${colors.cyan}Try running:${colors.reset} python LLM-Live2D-Desktop-Assitant-main/server.py`);
    } else if (activeServers === 1) {
        console.log(`${colors.bgGreen}${colors.bright} 1 ACTIVE SERVER FOUND ${colors.reset}`);
        console.log();
        console.log(`${colors.green}This is the expected configuration.${colors.reset}`);
        console.log(`The frontend should connect to this server.`);
    } else {
        console.log(`${colors.bgYellow}${colors.bright} ${activeServers} ACTIVE SERVERS FOUND! ${colors.reset}`);
        console.log();
        console.log(`${colors.yellow}Warning:${colors.reset} Multiple backend instances detected.`);
        console.log(`This can cause connection problems for the frontend.`);
        console.log();
        console.log(`${colors.cyan}Recommendation:${colors.reset}`);
        console.log(`1. Stop all Python processes: taskkill /F /IM python.exe`);
        console.log(`2. Delete server_port.txt: del LLM-Live2D-Desktop-Assitant-main\\server_port.txt`);
        console.log(`3. Start a single backend instance: python LLM-Live2D-Desktop-Assitant-main/server.py`);
    }
    
    console.log();
    console.log(`${colors.bright}${colors.cyan}====================================${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan}          DIAGNOSIS COMPLETE          ${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan}====================================${colors.reset}`);
});
