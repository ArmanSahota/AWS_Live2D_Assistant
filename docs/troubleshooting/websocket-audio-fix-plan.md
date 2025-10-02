# WebSocket Audio/Text Payload Fix Plan

## Problem Analysis

The issue occurs in the communication pipeline after AWS Bedrock responds:
1. **Backend receives AWS Bedrock response** ✅ (Working - shows in terminal)
2. **Backend prepares audio/text payload** ✅ (Working - `stream_audio.py`)
3. **Backend sends payload via WebSocket** ❌ (Issue here)
4. **Frontend receives and processes payload** ❌ (Never receives it)
5. **Subtitles stuck on "Thinking..."** ❌ (Result of not receiving payload)

## Root Cause

The WebSocket message handling has a critical issue in the async execution context:

### Current Problem in `server.py` (lines 217-221):
```python
async def _send_audio():
    await websocket.send_text(json.dumps(payload))
    await asyncio.sleep(duration)

asyncio.run_coroutine_threadsafe(_send_audio(), loop)
```

The issue is that `_websocket_audio_handler` is being called from a non-async context but tries to send data through an async WebSocket. The `asyncio.run_coroutine_threadsafe` might not be executing properly or the coroutine is failing silently.

## Technical Details

### Message Flow Breakdown:
1. **Port Detection**: WebSocket connects on port 8002 (server.py default) or dynamic port
2. **Message Types**:
   - `audio-payload`: Contains audio, text, volumes, expressions
   - `full-text`: Contains only text for subtitles
3. **Frontend Handlers**: 
   - `handleWebSocketMessage()` in `websocket.js`
   - `addAudioTask()` in `audio.js`
   - `displaySubtitles()` in `subtitle-handler.js`

## Solution Approach

### Fix 1: Ensure Proper Async Context (Priority: HIGH)
**File**: `server.py`, lines 195-223

The `_websocket_audio_handler` function needs to properly handle the async context:

```python
def _websocket_audio_handler(sentence, filepath, instrument_filepath=None):
    # ... existing code ...
    
    # Fix: Ensure the coroutine runs properly
    async def _send_audio():
        try:
            await websocket.send_text(json.dumps(payload))
            logger.info(f"Successfully sent audio payload with text: {sentence[:50]}...")
            await asyncio.sleep(duration)
        except Exception as e:
            logger.error(f"Failed to send audio payload: {e}")
    
    # Use create_task instead of run_coroutine_threadsafe
    if loop and loop.is_running():
        task = asyncio.create_task(_send_audio())
    else:
        # Fallback for thread safety
        future = asyncio.run_coroutine_threadsafe(_send_audio(), loop)
        try:
            future.result(timeout=5)  # Wait for completion with timeout
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")
```

### Fix 2: Add Debugging and Error Handling
**File**: `server.py`

Add comprehensive logging to track message flow:

```python
logger.info(f"Preparing to send audio payload - Text: {sentence[:50]}")
logger.info(f"Payload type: {payload.get('type')}, Format: {payload.get('format')}")
logger.info(f"Audio size: {len(payload.get('audio', ''))} bytes")
```

### Fix 3: Verify WebSocket Connection State
**File**: `server.py`

Check WebSocket state before sending:

```python
if websocket.client_state != WebSocketState.CONNECTED:
    logger.error("WebSocket not connected, cannot send audio payload")
    return
```

### Fix 4: Frontend Message Handler Verification
**File**: `static/desktop/websocket.js`

Ensure the message handler properly processes audio-payload:

```javascript
case 'audio-payload':
    console.log('[DEBUG] Full payload received:', JSON.stringify(data).substring(0, 200));
    // Verify all required fields
    if (!data.audio) {
        console.error('[ERROR] Missing audio data in payload');
        return;
    }
    // ... rest of handler
```

## Implementation Steps

### Step 1: Backend WebSocket Fix
1. Update `_websocket_audio_handler` in `server.py`
2. Add proper error handling and logging
3. Ensure coroutine execution completes

### Step 2: Add Message Tracing
1. Log every WebSocket send on backend
2. Log every WebSocket receive on frontend
3. Add sequence numbers to track message order

### Step 3: Frontend Resilience
1. Add fallback text display if audio fails
2. Implement timeout for "Thinking..." state
3. Add retry mechanism for failed messages

### Step 4: Testing Protocol
1. Send test message through WebSocket
2. Verify message arrives at frontend
3. Check audio and text processing separately
4. Monitor for async execution errors

## Quick Fix (Immediate)

For immediate testing, modify `server.py` line 217-221:

```python
# Replace the async sending with synchronous for testing
try:
    # Create a synchronous send task
    import threading
    def send_sync():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(websocket.send_text(json.dumps(payload)))
    
    thread = threading.Thread(target=send_sync)
    thread.start()
    thread.join(timeout=5)
    logger.info("Audio payload sent successfully")
except Exception as e:
    logger.error(f"Failed to send audio: {e}")
```

## Validation Tests

### Test 1: WebSocket Echo Test
```javascript
// In browser console
ws.send(JSON.stringify({type: 'test', message: 'echo'}));
```

### Test 2: Manual Audio Payload Test
```python
# In server.py, add test endpoint
@app.post("/test-audio")
async def test_audio():
    test_payload = {
        "type": "audio-payload",
        "text": "Test message",
        "audio": "base64_test_data",
        "volumes": [0.5],
        "slice_length": 0.1,
        "format": "mp3"
    }
    for client in connected_clients:
        await client.send_text(json.dumps(test_payload))
    return {"status": "sent"}
```

### Test 3: Message Flow Trace
Add timestamps and IDs to track message lifecycle:
```python
payload["message_id"] = str(uuid.uuid4())
payload["timestamp"] = time.time()
logger.info(f"Sending message {payload['message_id']}")
```

## Expected Outcome

After implementing these fixes:
1. ✅ Backend sends audio/text payload successfully
2. ✅ Frontend receives complete payload
3. ✅ Subtitles update from "Thinking..." to actual response
4. ✅ Audio plays with proper lip-sync
5. ✅ Full conversation flow works end-to-end

## Monitoring Points

1. **Backend Logs**: Look for "Successfully sent audio payload"
2. **Frontend Console**: Check for "Received audio-payload message"
3. **Network Tab**: Monitor WebSocket frames for payload
4. **Subtitle Element**: Verify text updates in DOM

## Alternative Approaches

If the async context fix doesn't work:

### Option A: Use Queue-Based Approach
- Queue messages in a list
- Have a separate async task consume and send

### Option B: Direct WebSocket Send
- Bypass the audio handler wrapper
- Send directly from the LLM response handler

### Option C: HTTP Fallback
- Send audio/text via HTTP POST
- Poll for responses instead of WebSocket push

## Next Steps

1. Apply Fix 1 (async context) first
2. Add comprehensive logging
3. Test with simple echo messages
4. Gradually test with full audio payloads
5. Monitor for race conditions or timing issues

## Related Files

- `server.py`: Lines 195-230 (WebSocket audio handler)
- `static/desktop/websocket.js`: Lines 215-240 (audio-payload handler)
- `static/desktop/audio.js`: Lines 1-40 (addAudioTask function)
- `tts/stream_audio.py`: Lines 40-91 (payload preparation)
- `module/openllm_vtuber_main.py`: Audio output function setup

## Success Criteria

The fix is successful when:
- User speaks → STT processes → LLM responds → TTS generates audio → Frontend receives payload → Subtitles show response → Audio plays → Lip-sync animates