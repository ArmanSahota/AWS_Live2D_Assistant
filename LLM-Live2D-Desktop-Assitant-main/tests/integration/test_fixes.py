#!/usr/bin/env python3
"""
Smoke test script to validate the applied fixes.
Tests server startup, port binding, CORS, and basic endpoints.
"""

import asyncio
import json
import requests
import websockets
import time
import sys
from loguru import logger

def test_server_health(port=1018):
    """Test if server health endpoint is accessible"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Health check passed: {data}")
            return True
        else:
            logger.error(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def test_static_files(port=1018):
    """Test if static files are accessible"""
    try:
        # Test CSS file
        response = requests.get(f"http://localhost:{port}/static/desktop/style.css", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Static CSS file accessible")
            css_success = True
        else:
            logger.error(f"❌ CSS file failed with status {response.status_code}")
            css_success = False
        
        # Test HTML file
        response = requests.get(f"http://localhost:{port}/static/desktop.html", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Static HTML file accessible")
            html_success = True
        else:
            logger.error(f"❌ HTML file failed with status {response.status_code}")
            html_success = False
            
        return css_success and html_success
    except Exception as e:
        logger.error(f"❌ Static file test failed: {e}")
        return False

async def test_websocket_connection(port=1018):
    """Test WebSocket connection and basic message exchange"""
    try:
        uri = f"ws://localhost:{port}/client-ws"
        logger.info(f"Testing WebSocket connection to {uri}")
        
        async with websockets.connect(uri) as websocket:
            # Wait for initial connection message
            message = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(message)
            
            if data.get("type") == "full-text" and "Connection established" in data.get("text", ""):
                logger.info("✅ WebSocket connection established successfully")
                
                # Test sending a simple message
                test_message = {"type": "text-input", "text": "Hello, this is a test"}
                await websocket.send(json.dumps(test_message))
                logger.info("✅ Test message sent successfully")
                
                return True
            else:
                logger.error(f"❌ Unexpected initial message: {data}")
                return False
                
    except asyncio.TimeoutError:
        logger.error("❌ WebSocket connection timed out")
        return False
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")
        return False

def test_cors_headers(port=1018):
    """Test if CORS headers are present"""
    try:
        response = requests.options(f"http://localhost:{port}/health", timeout=5)
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
        }
        
        if cors_headers['access-control-allow-origin'] == '*':
            logger.info("✅ CORS headers configured correctly")
            return True
        else:
            logger.warning(f"⚠️ CORS headers may not be optimal: {cors_headers}")
            return False
    except Exception as e:
        logger.error(f"❌ CORS test failed: {e}")
        return False

async def run_all_tests():
    """Run all smoke tests"""
    logger.info("🧪 Starting smoke tests for applied fixes...")
    
    # Find the server port (try common ports)
    ports_to_try = [1018, 1019, 1020, 1025, 1026, 1027, 1028, 1029]
    server_port = None
    
    for port in ports_to_try:
        if test_server_health(port):
            server_port = port
            logger.info(f"📡 Found server running on port {port}")
            break
    
    if not server_port:
        logger.error("❌ No server found on any expected port. Please start the server first.")
        return False
    
    # Run tests
    results = []
    
    # Test 1: Health endpoint
    results.append(("Health Check", test_server_health(server_port)))
    
    # Test 2: Static files
    results.append(("Static Files", test_static_files(server_port)))
    
    # Test 3: CORS headers
    results.append(("CORS Headers", test_cors_headers(server_port)))
    
    # Test 4: WebSocket connection
    ws_result = await test_websocket_connection(server_port)
    results.append(("WebSocket Connection", ws_result))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("🧪 SMOKE TEST RESULTS")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    logger.info("="*50)
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All smoke tests passed! The fixes appear to be working.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed. Please check the server configuration.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)