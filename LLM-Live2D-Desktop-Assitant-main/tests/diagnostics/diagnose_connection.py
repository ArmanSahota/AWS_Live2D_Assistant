#!/usr/bin/env python3
"""
Frontend-Backend Connection Diagnostic Tool
Identifies and fixes connection issues between Electron and Python server
"""

import os
import sys
import socket
import json
import time
import subprocess
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionDiagnostic:
    def __init__(self):
        self.issues_found = []
        self.server_port = None
        self.server_running = False
        
    def check_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def find_server_port(self) -> Optional[int]:
        """Find which port the server is running on"""
        # Check common ports
        common_ports = [8002, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025]
        
        for port in common_ports:
            if self.check_port_in_use(port):
                logger.info(f"Found service on port {port}")
                # Try to verify it's our server
                try:
                    import requests
                    response = requests.get(f"http://localhost:{port}/health", timeout=1)
                    if response.status_code == 200:
                        logger.info(f"✅ Server confirmed on port {port}")
                        return port
                except:
                    pass
        
        return None
    
    def check_server_port_file(self) -> Optional[int]:
        """Check server_port.txt file"""
        port_file = Path("server_port.txt")
        if port_file.exists():
            try:
                with open(port_file, 'r') as f:
                    port = int(f.read().strip())
                    logger.info(f"Port file exists: {port}")
                    return port
            except:
                logger.error("❌ Port file exists but is corrupted")
                self.issues_found.append("Corrupted server_port.txt file")
        else:
            logger.warning("⚠️ server_port.txt file not found")
            self.issues_found.append("Missing server_port.txt file")
        return None
    
    def check_python_server(self) -> bool:
        """Check if Python server is running"""
        # Check if python process is running
        try:
            result = subprocess.run(
                ['tasklist' if os.name == 'nt' else 'ps', 'aux'],
                capture_output=True,
                text=True
            )
            if 'python' in result.stdout.lower() and 'server.py' in result.stdout.lower():
                logger.info("✅ Python server process found")
                return True
            else:
                logger.error("❌ Python server process not found")
                self.issues_found.append("Python server not running")
                return False
        except:
            logger.warning("⚠️ Could not check process list")
            return False
    
    async def test_websocket_connection(self, port: int) -> bool:
        """Test WebSocket connection"""
        ws_url = f"ws://localhost:{port}/client-ws"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url, timeout=2) as ws:
                    logger.info(f"✅ WebSocket connection successful on port {port}")
                    
                    # Try to receive initial message
                    msg = await asyncio.wait_for(ws.receive(), timeout=2)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        logger.info(f"✅ Received initial message: {data.get('type', 'unknown')}")
                        return True
        except asyncio.TimeoutError:
            logger.error(f"❌ WebSocket connection timeout on port {port}")
            self.issues_found.append(f"WebSocket timeout on port {port}")
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.issues_found.append(f"WebSocket connection failed: {str(e)}")
        return False
    
    def check_firewall(self) -> None:
        """Check firewall settings (Windows)"""
        if os.name == 'nt':
            try:
                result = subprocess.run(
                    ['netsh', 'advfirewall', 'show', 'currentprofile'],
                    capture_output=True,
                    text=True
                )
                if 'State' in result.stdout and 'ON' in result.stdout:
                    logger.warning("⚠️ Windows Firewall is ON - may block connections")
                    self.issues_found.append("Windows Firewall enabled - may need exception")
            except:
                pass
    
    def check_electron_files(self) -> None:
        """Check if Electron files exist and are accessible"""
        critical_files = [
            "static/desktop.html",
            "static/desktop/websocket.js",
            "static/desktop/audio.js",
            "main.js"
        ]
        
        for file in critical_files:
            if not Path(file).exists():
                logger.error(f"❌ Missing critical file: {file}")
                self.issues_found.append(f"Missing file: {file}")
            else:
                logger.info(f"✅ Found: {file}")
    
    def create_port_file(self, port: int) -> None:
        """Create server_port.txt file"""
        try:
            with open("server_port.txt", "w") as f:
                f.write(str(port))
            logger.info(f"✅ Created server_port.txt with port {port}")
        except Exception as e:
            logger.error(f"❌ Failed to create port file: {e}")
    
    async def run_diagnostics(self):
        """Run all diagnostics"""
        logger.info("=" * 60)
        logger.info("FRONTEND-BACKEND CONNECTION DIAGNOSTIC")
        logger.info("=" * 60)
        
        # 1. Check if server is running
        logger.info("\n1. Checking Python server...")
        self.check_python_server()
        
        # 2. Find server port
        logger.info("\n2. Finding server port...")
        self.server_port = self.find_server_port()
        
        if not self.server_port:
            logger.error("❌ No server found on any port!")
            logger.info("\n🔧 FIX: Start the server with:")
            logger.info("   cd LLM-Live2D-Desktop-Assitant-main")
            logger.info("   python server.py")
            return
        
        # 3. Check port file
        logger.info("\n3. Checking port file...")
        file_port = self.check_server_port_file()
        
        if file_port != self.server_port:
            logger.warning(f"⚠️ Port mismatch! File: {file_port}, Actual: {self.server_port}")
            self.create_port_file(self.server_port)
        
        # 4. Test WebSocket
        logger.info("\n4. Testing WebSocket connection...")
        ws_ok = await self.test_websocket_connection(self.server_port)
        
        # 5. Check firewall
        logger.info("\n5. Checking firewall...")
        self.check_firewall()
        
        # 6. Check Electron files
        logger.info("\n6. Checking Electron files...")
        self.check_electron_files()
        
        # Report
        logger.info("\n" + "=" * 60)
        logger.info("DIAGNOSTIC RESULTS")
        logger.info("=" * 60)
        
        if not self.issues_found:
            logger.info("✅ No issues found! Connection should work.")
            logger.info(f"\n📡 Server is running on port: {self.server_port}")
            logger.info("📁 server_port.txt is correct")
            logger.info("🔌 WebSocket connection is working")
            logger.info("\n✨ Try refreshing the Electron app (Ctrl+R)")
        else:
            logger.error(f"❌ Found {len(self.issues_found)} issues:")
            for i, issue in enumerate(self.issues_found, 1):
                logger.error(f"   {i}. {issue}")
            
            logger.info("\n🔧 FIXES:")
            
            if "Python server not running" in str(self.issues_found):
                logger.info("\n1. Start the server:")
                logger.info("   cd LLM-Live2D-Desktop-Assitant-main")
                logger.info("   python server.py")
            
            if "WebSocket" in str(self.issues_found):
                logger.info("\n2. Check WebSocket in browser console:")
                logger.info("   ws = new WebSocket('ws://localhost:8002/client-ws')")
                logger.info("   ws.onopen = () => console.log('Connected!')")
            
            if "Firewall" in str(self.issues_found):
                logger.info("\n3. Add firewall exception (Windows):")
                logger.info("   netsh advfirewall firewall add rule name=\"VTuber Server\" dir=in action=allow protocol=TCP localport=8002")
            
            if "Missing file" in str(self.issues_found):
                logger.info("\n4. Ensure you're in the correct directory")
                logger.info("   Some files may be missing or in wrong location")
        
        # Quick fix script
        logger.info("\n" + "=" * 60)
        logger.info("QUICK FIX COMMANDS")
        logger.info("=" * 60)
        logger.info("Run these in order:")
        logger.info(f"1. echo {self.server_port} > server_port.txt")
        logger.info("2. npm start  (or restart Electron app)")
        logger.info("3. In Electron console: location.reload()")

def create_test_html():
    """Create a simple HTML test page"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Connection Test</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background: #4CAF50; color: white; }
        .disconnected { background: #f44336; color: white; }
        .log { background: #f0f0f0; padding: 10px; height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status" class="status disconnected">Disconnected</div>
    <button onclick="connect()">Connect</button>
    <button onclick="testMessage()">Send Test</button>
    <button onclick="clearLog()">Clear Log</button>
    <div id="log" class="log"></div>
    
    <script>
        let ws = null;
        const log = document.getElementById('log');
        const status = document.getElementById('status');
        
        function addLog(msg) {
            const time = new Date().toLocaleTimeString();
            log.innerHTML += `[${time}] ${msg}<br>`;
            log.scrollTop = log.scrollHeight;
        }
        
        async function findPort() {
            // Try to read port file
            try {
                const response = await fetch('/server_port.txt');
                if (response.ok) {
                    const port = await response.text();
                    return parseInt(port.trim());
                }
            } catch (e) {}
            
            // Try common ports
            const ports = [8002, 1018, 1019, 1020];
            for (const port of ports) {
                try {
                    const response = await fetch(`http://localhost:${port}/health`);
                    if (response.ok) {
                        return port;
                    }
                } catch (e) {}
            }
            return 8002; // default
        }
        
        async function connect() {
            const port = await findPort();
            addLog(`Connecting to port ${port}...`);
            
            ws = new WebSocket(`ws://localhost:${port}/client-ws`);
            
            ws.onopen = () => {
                addLog('✅ Connected!');
                status.textContent = 'Connected';
                status.className = 'status connected';
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                addLog(`📥 Received: ${data.type} - ${JSON.stringify(data).substring(0, 100)}...`);
            };
            
            ws.onerror = (error) => {
                addLog(`❌ Error: ${error}`);
            };
            
            ws.onclose = () => {
                addLog('❌ Disconnected');
                status.textContent = 'Disconnected';
                status.className = 'status disconnected';
            };
        }
        
        function testMessage() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const msg = {type: 'test', message: 'Hello from test page'};
                ws.send(JSON.stringify(msg));
                addLog(`📤 Sent: ${JSON.stringify(msg)}`);
            } else {
                addLog('❌ Not connected');
            }
        }
        
        function clearLog() {
            log.innerHTML = '';
        }
        
        // Auto-connect on load
        window.onload = () => {
            setTimeout(connect, 500);
        };
    </script>
</body>
</html>"""
    
    with open("LLM-Live2D-Desktop-Assitant-main/test_connection.html", "w") as f:
        f.write(html_content)
    logger.info("✅ Created test_connection.html - Open in browser to test")

async def main():
    diagnostic = ConnectionDiagnostic()
    await diagnostic.run_diagnostics()
    
    # Create test HTML
    create_test_html()
    
    logger.info("\n" + "=" * 60)
    logger.info("ADDITIONAL TESTING")
    logger.info("=" * 60)
    logger.info("1. Open test_connection.html in browser")
    logger.info("2. Check if WebSocket connects")
    logger.info("3. Try sending test messages")
    logger.info("\nIf test page works but Electron doesn't:")
    logger.info("- Issue is with Electron configuration")
    logger.info("- Check preload.js and main.js files")

if __name__ == "__main__":
    asyncio.run(main())