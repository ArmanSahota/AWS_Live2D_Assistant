#!/usr/bin/env python3
"""
Fix the STT pipeline by ensuring proper WebSocket communication
"""

import json
import asyncio
import websockets
import numpy as np
from loguru import logger

async def test_websocket_stt():
    """Test WebSocket connection and STT pipeline"""
    uri = "ws://localhost:1018/client-ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket")
            
            # Wait for initial messages
            response = await websocket.recv()
            logger.info(f"Initial response: {response}")
            
            # Send a test text message
            test_message = {
                "type": "text-input",
                "text": "Hello, can you hear me?"
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("Sent test message")
            
            # Wait for response
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                logger.info(f"Received: {data.get('type')}")
                
                if data.get('type') == 'audio-data':
                    logger.info("Received audio response!")
                    break
                    
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    print("Testing WebSocket STT Pipeline...")
    asyncio.run(test_websocket_stt())