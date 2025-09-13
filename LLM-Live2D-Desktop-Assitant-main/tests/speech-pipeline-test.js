/**
 * Speech Pipeline Test Script
 * 
 * This script tests each component of the speech pipeline to help diagnose issues.
 * Run this script from the DevTools console in the Electron app.
 */

// Test configuration
const TEST_TEXT = "This is a test of the speech pipeline.";
const CLAUDE_TEST_PROMPT = "Say hello in a friendly way.";

// Test results storage
const testResults = {
  config: null,
  health: null,
  claudeApi: null,
  tts: null,
  stt: null,
  fullPipeline: null
};

// Helper function to log test results
function logTestResult(test, success, details = null) {
  const status = success ? '✅ PASS' : '❌ FAIL';
  console.log(`[TEST] ${test}: ${status}`);
  if (details) {
    console.log(`[TEST] Details: ${JSON.stringify(details)}`);
  }
  testResults[test] = { success, details };
}

// Test configuration
async function testConfig() {
  try {
    console.log('[TEST] Testing configuration...');
    const config = await window.api.getConfig();
    const httpBase = config.httpBase;
    
    if (!httpBase) {
      logTestResult('config', false, { error: 'HTTP_BASE not configured' });
      return false;
    }
    
    logTestResult('config', true, { httpBase });
    return true;
  } catch (error) {
    logTestResult('config', false, { error: error.message });
    return false;
  }
}

// Test health endpoint
async function testHealth() {
  try {
    console.log('[TEST] Testing health endpoint...');
    const health = await window.api.getHealth();
    
    if (health.status !== 'ok') {
      logTestResult('health', false, health);
      return false;
    }
    
    logTestResult('health', true, health);
    return true;
  } catch (error) {
    logTestResult('health', false, { error: error.message });
    return false;
  }
}

// Test Claude API
async function testClaudeApi() {
  try {
    console.log('[TEST] Testing Claude API...');
    console.log(`[TEST] Sending prompt: "${CLAUDE_TEST_PROMPT}"`);
    
    const response = await window.api.askClaude(CLAUDE_TEST_PROMPT);
    
    if (!response) {
      logTestResult('claudeApi', false, { error: 'Empty response' });
      return false;
    }
    
    logTestResult('claudeApi', true, { response: response.substring(0, 50) + (response.length > 50 ? '...' : '') });
    return true;
  } catch (error) {
    logTestResult('claudeApi', false, { error: error.message });
    return false;
  }
}

// Test TTS
async function testTTS() {
  try {
    console.log('[TEST] Testing TTS...');
    console.log(`[TEST] Generating speech for: "${TEST_TEXT}"`);
    
    const speechData = await window.api.generateSpeech(TEST_TEXT);
    
    if (!speechData || !speechData.base64) {
      logTestResult('tts', false, { error: 'No speech data generated' });
      return false;
    }
    
    // Try to play the audio
    try {
      const audio = new Audio(`data:${speechData.mime};base64,${speechData.base64}`);
      audio.play();
    } catch (playError) {
      console.warn('[TEST] Could not auto-play audio:', playError);
    }
    
    logTestResult('tts', true, { 
      audioSize: speechData.base64.length,
      mime: speechData.mime
    });
    return true;
  } catch (error) {
    logTestResult('tts', false, { error: error.message });
    return false;
  }
}

// Test STT (manual test)
function testSTT() {
  console.log('[TEST] Testing STT...');
  console.log('[TEST] Please speak into your microphone. Your transcription will appear below.');
  
  // Store the original transcription history length
  let originalLength = 0;
  
  // Get the current transcription history
  window.api.getTranscriptionHistory().then(history => {
    originalLength = history.length;
    
    // Set up a check after 10 seconds
    setTimeout(async () => {
      const newHistory = await window.api.getTranscriptionHistory();
      const newTranscriptions = newHistory.slice(originalLength);
      
      if (newTranscriptions.length === 0) {
        logTestResult('stt', false, { error: 'No transcriptions detected in 10 seconds' });
      } else {
        logTestResult('stt', true, { 
          transcriptions: newTranscriptions.map(t => t.text)
        });
      }
    }, 10000);
  });
  
  // Manually trigger STT if needed
  if (window.start_mic) {
    window.start_mic();
  }
  
  return "STT test in progress... please speak into your microphone";
}

// Test full pipeline
async function testFullPipeline() {
  console.log('[TEST] Testing full pipeline...');
  console.log('[TEST] This will simulate the entire speech-to-response pipeline');
  
  try {
    // Simulate STT result
    console.log('[TEST] Simulating speech transcription...');
    window.logSTTResult(TEST_TEXT);
    
    // Wait for the pipeline to complete
    console.log('[TEST] Waiting for pipeline to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check path ping status
    const pipelineStatus = { ...window.pathStatus };
    
    // Check if any steps failed
    const failedSteps = Object.entries(pipelineStatus)
      .filter(([key, value]) => value === false)
      .map(([key]) => key);
    
    if (failedSteps.length > 0) {
      logTestResult('fullPipeline', false, { 
        failedSteps,
        pipelineStatus
      });
      return false;
    }
    
    logTestResult('fullPipeline', true, { pipelineStatus });
    return true;
  } catch (error) {
    logTestResult('fullPipeline', false, { error: error.message });
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('=== SPEECH PIPELINE TEST SUITE ===');
  
  // Run tests in sequence
  await testConfig();
  await testHealth();
  await testClaudeApi();
  await testTTS();
  console.log(testSTT()); // This is async but doesn't return a promise
  await testFullPipeline();
  
  // Print summary
  console.log('\n=== TEST SUMMARY ===');
  Object.entries(testResults).forEach(([test, result]) => {
    if (result) {
      const status = result.success ? '✅ PASS' : '❌ FAIL';
      console.log(`${test}: ${status}`);
    } else {
      console.log(`${test}: ⚠️ NOT RUN`);
    }
  });
  
  return testResults;
}

// Export functions for individual testing
window.speechTests = {
  testConfig,
  testHealth,
  testClaudeApi,
  testTTS,
  testSTT,
  testFullPipeline,
  runAllTests
};

console.log('Speech pipeline test script loaded. Run tests with:');
console.log('window.speechTests.runAllTests()');
console.log('Or run individual tests with window.speechTests.testXxx()');
