# Testing Guide: Live2D Auto-Initialization and LLM Separation

This guide outlines the testing procedures to verify that the Live2D model auto-initializes correctly when the Electron app loads and that it's properly separated from the LLM.

## 1. Testing Live2D Auto-Initialization

### Test Case 1.1: Normal Startup
1. Launch the Electron application
2. Observe the console logs
3. **Expected Result**: 
   - You should see "Initializing Live2D model on page load" in the console
   - The Live2D model should appear within 1-2 seconds of the app window appearing
   - The message "Live2D model loaded successfully" should appear in logs

### Test Case 1.2: Disconnected Server Startup
1. Ensure the WebSocket server is not running
2. Launch the Electron application
3. **Expected Result**:
   - The Live2D model should still initialize and appear
   - You may see WebSocket connection errors in the console, but they should not prevent the model from loading

### Test Case 1.3: Model Fallback
1. Temporarily rename the default model folder
2. Launch the Electron application
3. **Expected Result**:
   - The app should try alternative paths to find a model
   - Either a fallback model should load or an error message should be shown
4. Restore the original folder name after testing

### Test Case 1.4: Model Loading Performance
1. Launch the Electron application with Developer Tools open
2. Check the Performance tab timeline
3. **Expected Result**:
   - Model initialization should start immediately after DOM content loaded
   - Total loading time should be reasonable (under 2 seconds on most systems)

## 2. Testing Live2D and LLM Separation

### Test Case 2.1: STT to LLM Flow
1. Launch the application with both the WebSocket server and model loaded
2. Click the "Test STT" button
3. Speak into the microphone
4. **Expected Result**:
   - The transcribed text should appear in the console
   - The text should be sent to the LLM without affecting the model
   - The path ping status should show 'stt' and 'stt-to-claude' as true

### Test Case 2.2: LLM to TTS Flow
1. Click the "Test Claude API" button
2. **Expected Result**:
   - Claude should respond with text
   - The text should be sent to TTS without affecting the model
   - The path ping status should show 'claude-response' and 'tts-generation' as true

### Test Case 2.3: TTS to Live2D Animation
1. Click the "Test Full Pipeline" button
2. **Expected Result**:
   - The full pipeline should execute from text to LLM to TTS to animation
   - The Live2D model's mouth should animate in sync with the audio
   - The path ping status should show all steps completed successfully

### Test Case 2.4: WebSocket Connection Loss During Speech
1. Start the full pipeline test
2. During TTS playback, disconnect the WebSocket server
3. **Expected Result**:
   - The audio should continue playing
   - The Live2D model should continue animating
   - The application should attempt to reconnect in the background

### Test Case 2.5: Independent Model Control
1. Open the browser console
2. Execute direct commands to the Live2D controller:
   ```javascript
   window.live2dController.setMouth(0.5);
   window.live2dController.setExpression(1);
   window.live2dController.resetToIdle();
   ```
3. **Expected Result**:
   - The model should respond directly to these commands
   - No errors should appear in the console
   - No WebSocket or LLM communication should occur

## 3. Edge Case Testing

### Test Case 3.1: Multiple Audio Playbacks
1. Click the "Test TTS" button multiple times in quick succession
2. **Expected Result**:
   - Audio tasks should queue properly
   - The model should animate for each audio segment
   - No visual glitches in the animation

### Test Case 3.2: Audio Interruption
1. Start a TTS playback with the "Test TTS" button
2. Quickly interrupt with new audio by clicking "Test TTS" again
3. **Expected Result**:
   - The first audio should stop
   - The model animation should smoothly transition to the new audio
   - No animation artifacts should be visible

### Test Case 3.3: Model Switching
1. Use the "Switch Model" dropdown to select a different model
2. **Expected Result**:
   - The new model should load independently
   - The system should remain functional after the switch
   - Speech animation should still work properly

## 4. Performance Testing

### Test Case 4.1: Memory Usage
1. Run the application for an extended period (30+ minutes)
2. Monitor memory usage in Task Manager or Activity Monitor
3. **Expected Result**:
   - Memory usage should remain stable
   - No significant memory leaks should occur

### Test Case 4.2: CPU Usage During Animation
1. Play several audio segments with animations
2. Monitor CPU usage
3. **Expected Result**:
   - CPU spikes should be minimal during animation
   - The animation should remain smooth

## 5. Regression Testing

### Test Case 5.1: Original Features
1. Test all original features of the application
2. **Expected Result**:
   - All pre-existing functionality should continue to work
   - No regressions in any area of the application

## Reporting Issues

If any test fails, document the following:
1. Test case number and description
2. Expected behavior
3. Actual behavior
4. Console logs or errors
5. Screenshots if applicable
6. Steps to reproduce

## Fixes for Common Issues

### Live2D Model Not Loading
- Check if the model path is correctly resolved
- Verify that all model files are present
- Check if the `live2dModule.init()` is being called

### Animation Not Syncing with Audio
- Check if the `animate` function is receiving proper data
- Verify that audio duration calculation is accurate
- Increase the logging for animation frames

### WebSocket Connection Issues
- Verify the server is running on the expected port
- Check for network restrictions or firewalls
- Try reconnecting with the built-in reconnect function