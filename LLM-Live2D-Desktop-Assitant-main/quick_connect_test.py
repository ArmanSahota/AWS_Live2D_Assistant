#!/usr/bin/env python3
"""
Quick Connection Test Script
Tests which port the server is running on and verifies WebSocket connectivity
"""

import socket
import requests
import json
import sys
from typing import Optional

def check_port(port: int) -> bool:
    """Check if a port has a service listening"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        if response.status_code == 200:
            print(f"✅ Found server on port {port}")
            data = response.json()
            print(f"   Server info: {data}")
            return True
    except:
        pass
    return False

def find_server() -> Optional[int]:
    """Find which port the server is running on"""
    print("Scanning for server...")
    
    # Check common ports
    ports_to_check = [
        8000, 8001, 8002,  # New port manager defaults
        1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025  # Legacy ports
    ]
    
    for port in ports_to_check:
        if check_port(port):
            return port
    
    print("❌ No server found on any port")
    return None

def update_port_file(port: int):
    """Update the server_port.txt file"""
    try:
        with open("server_port.txt", "w") as f:
            f.write(str(port))
        print(f"✅ Updated server_port.txt with port {port}")
    except Exception as e:
        print(f"❌ Could not update port file: {e}")

def test_websocket(port: int):
    """Test WebSocket connection"""
    import asyncio
    import websockets
    
    async def test():
        uri = f"ws://localhost:{port}/client-ws"
        try:
            async with websockets.connect(uri, timeout=2) as websocket:
                print(f"✅ WebSocket connected to {uri}")
                
                # Try to receive initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=2)
                data = json.loads(message)
                print(f"✅ Received initial message: {data.get('type', 'unknown')}")
                return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    return asyncio.run(test())

def main():
    print("=" * 60)
    print("QUICK CONNECTION TEST")
    print("=" * 60)
    
    # Find server
    port = find_server()
    
    if not port:
        print("\n❌ Server not running!")
        print("\n📝 To start the server:")
        print("   cd LLM-Live2D-Desktop-Assitant-main")
        print("   python server.py")
        sys.exit(1)
    
    print(f"\n✅ Server found on port {port}")
    
    # Update port file
    update_port_file(port)
    
    # Test WebSocket
    print("\nTesting WebSocket connection...")
    if test_websocket(port):
        print("\n✅ WebSocket connection successful!")
    else:
        print("\n❌ WebSocket connection failed")
    
    print("\n" + "=" * 60)
    print("CONNECTION TEST COMPLETE")
    print("=" * 60)
    print(f"\n✅ Server is running on port: {port}")
    print("✅ server_port.txt has been updated")
    print("\n📝 Next steps:")
    print("1. Refresh the Electron app (Ctrl+R or Cmd+R)")
    print("2. Check the browser console for connection logs")
    print("3. The WebSocket should now connect automatically")
    
    print("\n💡 If still not connecting, open browser console and run:")
    print(f"   ws = new WebSocket('ws://localhost:{port}/client-ws')")
    print("   ws.onopen = () => console.log('Connected!')")
    print("   ws.onmessage = (e) => console.log('Message:', e.data)")

if __name__ == "__main__":
    main()