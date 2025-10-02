# WebSocket Audio/Text Payload Fix - TODO List

## 🔴 Critical Issues to Fix

### 1. Fix Async Context in WebSocket Audio Handler
- [ ] Update `server.py` lines 217-221 to properly handle async execution
- [ ] Add error handling and logging for WebSocket send operations
- [ ] Verify coroutine completion with timeout
- [ ] Test with both `asyncio.create_task()` and `run_coroutine_threadsafe()`

### 2. Add Comprehensive Logging
- [ ] Log when AWS Bedrock response is received
- [ ] Log when TTS audio is generated
- [ ] Log when payload is prepared
- [ ] Log when WebSocket send is attempted
- [ ] Log when WebSocket send succeeds/fails
- [ ] Add message IDs for tracking

### 3. Verify WebSocket Connection State
- [ ] Check WebSocket state before sending messages
- [ ] Add reconnection logic if connection is lost
- [ ] Implement heartbeat/ping-pong mechanism
- [ ] Handle WebSocket disconnection gracefully

## 🟡 Frontend Improvements

### 4. Enhanced Message Handler
- [ ] Add detailed logging in `handleWebSocketMessage()`
- [ ] Verify all required fields in audio-payload
- [ ] Add fallback for missing audio data
- [ ] Implement timeout for "Thinking..." state

### 5. Subtitle Display Fix
- [ ] Ensure `displaySubtitles()` function is always available
- [ ] Add direct DOM manipulation as fallback
- [ ] Remove any hidden classes when displaying text
- [ ] Force style recalculation after text update

### 6. Audio Task Queue Verification
- [ ] Verify `addAudioTask()` is properly initialized
- [ ] Check audio queue is not blocked
- [ ] Add error handling in audio playback
- [ ] Log audio task lifecycle

## 🟢 Testing & Validation

### 7. Create Test Endpoints
- [ ] Add `/test-websocket` endpoint for echo testing
- [ ] Add `/test-audio-payload` endpoint for manual testing
- [ ] Create test script to simulate full conversation flow
- [ ] Add WebSocket frame inspection tools

### 8. Message Flow Tracing
- [ ] Add sequence numbers to messages
- [ ] Log timestamps at each stage
- [ ] Create message flow visualization
- [ ] Monitor for dropped messages

### 9. Performance Monitoring
- [ ] Measure WebSocket latency
- [ ] Track message delivery success rate
- [ ] Monitor memory usage during streaming
- [ ] Check for async task leaks

## 📝 Implementation Order

### Phase 1: Immediate Fix (30 minutes)
1. [ ] Apply async context fix in `server.py`
2. [ ] Add basic error logging
3. [ ] Test with simple echo message
4. [ ] Verify WebSocket connection works

### Phase 2: Enhanced Debugging (1 hour)
5. [ ] Add comprehensive logging throughout pipeline
6. [ ] Implement message ID tracking
7. [ ] Add frontend console debugging
8. [ ] Create test endpoints

### Phase 3: Robustness (1 hour)
9. [ ] Implement connection state checking
10. [ ] Add retry mechanisms
11. [ ] Handle edge cases
12. [ ] Add timeout handling

### Phase 4: Testing (30 minutes)
13. [ ] Run end-to-end conversation test
14. [ ] Test with various response sizes
15. [ ] Test connection recovery
16. [ ] Verify subtitle updates

## 🔧 Quick Fix Code Snippets

### Backend Fix (server.py):
```python
# Line 217-221 replacement
async def _send_audio():
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(payload))
            logger.info(f"✅ Sent audio payload: {sentence[:30]}...")
        else:
            logger.error("❌ WebSocket not connected")
    except Exception as e:
        logger.error(f"❌ Send failed: {e}")

# Better async execution
if loop and loop.is_running():
    task = asyncio.create_task(_send_audio())
else:
    future = asyncio.run_coroutine_threadsafe(_send_audio(), loop)
    future.add_done_callback(lambda f: logger.info(f"Send complete: {f.result()}"))
```

### Frontend Debug (websocket.js):
```javascript
case 'audio-payload':
    console.log('🎵 Audio payload received:', {
        hasAudio: !!data.audio,
        audioSize: data.audio?.length || 0,
        text: data.text,
        timestamp: new Date().toISOString()
    });
    
    // Ensure subtitle updates even if audio fails
    if (data.text) {
        window.displaySubtitles?.(data.text);
    }
    
    // Process audio
    if (window.addAudioTask && data.audio) {
        window.addAudioTask(/* params */);
    } else {
        console.error('❌ Cannot process audio:', {
            hasFunction: !!window.addAudioTask,
            hasAudio: !!data.audio
        });
    }
    break;
```

## 🎯 Success Metrics

- [ ] WebSocket messages arrive within 100ms
- [ ] Subtitles update immediately after LLM response
- [ ] Audio plays without delay
- [ ] No "Thinking..." stuck states
- [ ] 100% message delivery success rate
- [ ] Graceful handling of connection issues

## 🚨 Common Pitfalls to Avoid

1. **Don't** assume WebSocket is always connected
2. **Don't** ignore async execution context
3. **Don't** forget to handle errors in coroutines
4. **Don't** block the event loop
5. **Don't** send messages without checking state

## 📊 Testing Checklist

- [ ] Test with short responses (< 10 words)
- [ ] Test with long responses (> 100 words)
- [ ] Test with special characters in text
- [ ] Test with rapid consecutive messages
- [ ] Test connection loss and recovery
- [ ] Test with multiple client connections
- [ ] Test with slow network conditions

## 🔍 Debugging Commands

### Backend (Python):
```python
# Add to server.py for debugging
import traceback
logger.add("websocket_debug.log", level="DEBUG")

# In _websocket_audio_handler
logger.debug(f"Stack trace: {traceback.format_stack()}")
```

### Frontend (JavaScript):
```javascript
// Add to console for debugging
window.wsDebug = true;
window.wsMessages = [];

// In handleWebSocketMessage
if (window.wsDebug) {
    window.wsMessages.push({
        time: Date.now(),
        type: data.type,
        data: data
    });
}
```

## 📚 Related Documentation

- [WebSocket Connection Fix](WEBSOCKET_CONNECTION_FIX.md)
- [Audio Wake Word Fix](AUDIO_WAKE_WORD_FIX_README.md)
- [Architecture Diagram](ARCHITECTURE_DIAGRAM.md)
- [Pipeline Integration Fixes](PIPELINE_INTEGRATION_FIXES.md)

## ✅ Definition of Done

The issue is resolved when:
1. User speaks to the assistant
2. Backend processes through AWS Bedrock
3. TTS generates audio response
4. WebSocket delivers payload to frontend
5. Subtitles immediately show the response text
6. Audio plays with proper lip-sync
7. No errors in console or logs
8. Works consistently across multiple interactions