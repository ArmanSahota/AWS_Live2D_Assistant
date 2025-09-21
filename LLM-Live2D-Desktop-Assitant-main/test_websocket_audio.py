#!/usr/bin/env python3
"""
WebSocket Audio Payload Test Script
Tests the WebSocket connection and audio payload delivery
"""

import asyncio
import json
import aiohttp
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection and audio payload delivery"""
    
    # Server configuration
    SERVER_URL = "http://localhost:8002"  # Adjust port if needed
    WS_URL = "ws://localhost:8002/client-ws"
    
    logger.info("=" * 60)
    logger.info("WebSocket Audio Payload Test")
    logger.info("=" * 60)
    
    # Step 1: Check server health
    logger.info("\n1. Checking server health...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Server is healthy: {data}")
                else:
                    logger.error(f"❌ Server health check failed: {response.status}")
                    return
    except Exception as e:
        logger.error(f"❌ Cannot connect to server: {e}")
        logger.info("Make sure the server is running on the correct port")
        return
    
    # Step 2: Test the test-audio-payload endpoint
    logger.info("\n2. Testing audio payload endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/test-audio-payload") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Test payload sent: {data}")
                else:
                    logger.error(f"❌ Test payload failed: {response.status}")
    except Exception as e:
        logger.error(f"❌ Test payload error: {e}")
    
    # Step 3: Connect to WebSocket and listen for messages
    logger.info("\n3. Connecting to WebSocket...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(WS_URL) as ws:
                logger.info("✅ WebSocket connected")
                
                # Send a test message
                test_msg = {
                    "type": "test",
                    "message": "WebSocket test from Python client",
                    "timestamp": datetime.now().isoformat()
                }
                await ws.send_str(json.dumps(test_msg))
                logger.info(f"📤 Sent test message: {test_msg}")
                
                # Listen for messages for 10 seconds
                logger.info("\n4. Listening for messages (10 seconds)...")
                timeout = 10
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            msg_type = data.get('type', 'unknown')
                            
                            if msg_type == 'audio-payload':
                                logger.info(f"✅ Received audio-payload!")
                                logger.info(f"   Text: {data.get('text', 'N/A')}")
                                logger.info(f"   Audio size: {len(data.get('audio', ''))} bytes")
                                logger.info(f"   Format: {data.get('format', 'N/A')}")
                            else:
                                logger.info(f"📥 Received {msg_type}: {str(data)[:100]}...")
                                
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f'❌ WebSocket error: {ws.exception()}')
                            break
                            
                    except asyncio.TimeoutError:
                        # No message received in 1 second, continue
                        pass
                    except Exception as e:
                        logger.error(f"❌ Error receiving message: {e}")
                        break
                
                logger.info("\n✅ Test completed")
                
    except Exception as e:
        logger.error(f"❌ WebSocket connection error: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary:")
    logger.info("- Check if server logs show '✅ Successfully sent audio payload'")
    logger.info("- Check if Electron console shows '[AUDIO DEBUG] ✅ Received audio-payload'")
    logger.info("- Check if subtitles update from 'Thinking...' to actual text")
    logger.info("=" * 60)

async def send_test_conversation():
    """Send a test conversation message to trigger the full pipeline"""
    
    WS_URL = "ws://localhost:8002/client-ws"
    
    logger.info("\n" + "=" * 60)
    logger.info("Sending Test Conversation")
    logger.info("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(WS_URL) as ws:
                logger.info("✅ Connected to WebSocket")
                
                # Wait for initial messages
                for _ in range(3):
                    msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        logger.info(f"📥 Initial: {data.get('type', 'unknown')}")
                
                # Send a text message to trigger LLM response
                test_text = {
                    "type": "text-input",
                    "text": "Hello, can you hear me? Please respond with a short greeting.",
                    "timestamp": datetime.now().isoformat()
                }
                
                await ws.send_str(json.dumps(test_text))
                logger.info(f"📤 Sent text: {test_text['text']}")
                
                # Listen for response
                logger.info("\nListening for LLM response (30 seconds)...")
                timeout = 30
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            msg_type = data.get('type', 'unknown')
                            
                            if msg_type == 'audio-payload':
                                logger.info(f"🎉 SUCCESS! Received audio-payload with text: {data.get('text', 'N/A')}")
                                return True
                            else:
                                logger.info(f"📥 {msg_type}: {str(data)[:100]}...")
                                
                    except asyncio.TimeoutError:
                        pass
                
                logger.warning("⏱️ Timeout - No audio-payload received")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    
    # Run basic connection test
    await test_websocket_connection()
    
    # Ask if user wants to test full conversation
    print("\nDo you want to test a full conversation? (y/n): ", end="")
    if input().lower() == 'y':
        success = await send_test_conversation()
        if success:
            logger.info("\n✅ Full conversation test PASSED!")
        else:
            logger.info("\n❌ Full conversation test FAILED - Check server logs for errors")

if __name__ == "__main__":
    asyncio.run(main())