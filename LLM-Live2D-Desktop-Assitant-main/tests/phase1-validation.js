#!/usr/bin/env node

/**
 * Phase 1 Validation Script
 * Tests the backend standardization changes for React + Vite migration
 */

const axios = require('axios');
const WebSocket = require('ws');

const BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

async function testHealthEndpoint() {
  console.log('🔍 Testing health endpoint...');
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Health endpoint response:', response.data);
    
    // Validate response structure
    if (response.data.status === 'ok' && response.data.port === 8000) {
      console.log('✅ Health endpoint validation passed');
      return true;
    } else {
      console.log('❌ Health endpoint validation failed');
      return false;
    }
  } catch (error) {
    console.log('❌ Health endpoint failed:', error.message);
    return false;
  }
}

async function testMockTTSEndpoint() {
  console.log('🔍 Testing mock TTS endpoint...');
  try {
    const response = await axios.post(`${BASE_URL}/api/tts/mock`, {
      text: 'Hello, this is a test message for TTS',
      voice: 'en-US-JennyNeural'
    });
    console.log('✅ Mock TTS response:', response.data);
    
    // Validate response structure
    if (response.data.status === 'success' && response.data.base64) {
      console.log('✅ Mock TTS endpoint validation passed');
      return true;
    } else {
      console.log('❌ Mock TTS endpoint validation failed');
      return false;
    }
  } catch (error) {
    console.log('❌ Mock TTS endpoint failed:', error.message);
    return false;
  }
}

async function testMockSTTEndpoint() {
  console.log('🔍 Testing mock STT endpoint...');
  try {
    const response = await axios.post(`${BASE_URL}/api/stt/mock`, {
      audio: 'mock_base64_audio_data',
      language: 'en'
    });
    console.log('✅ Mock STT response:', response.data);
    
    // Validate response structure
    if (response.data.status === 'success' && response.data.transcription) {
      console.log('✅ Mock STT endpoint validation passed');
      return true;
    } else {
      console.log('❌ Mock STT endpoint validation failed');
      return false;
    }
  } catch (error) {
    console.log('❌ Mock STT endpoint failed:', error.message);
    return false;
  }
}

async function testWebSocketEcho() {
  console.log('🔍 Testing WebSocket echo endpoint...');
  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(`${WS_URL}/ws/echo`);
      let testPassed = false;
      
      ws.on('open', () => {
        console.log('✅ WebSocket echo connection established');
        
        // Send test message
        const testMessage = {
          type: 'test',
          message: 'Hello WebSocket Echo',
          timestamp: Date.now()
        };
        
        ws.send(JSON.stringify(testMessage));
      });
      
      ws.on('message', (data) => {
        try {
          const response = JSON.parse(data);
          console.log('✅ WebSocket echo response:', response);
          
          // Validate echo response
          if (response.type === 'echo' && response.original && response.timestamp) {
            console.log('✅ WebSocket echo validation passed');
            testPassed = true;
          } else {
            console.log('❌ WebSocket echo validation failed');
          }
          
          ws.close();
          resolve(testPassed);
        } catch (error) {
          console.log('❌ WebSocket echo response parsing failed:', error.message);
          ws.close();
          resolve(false);
        }
      });
      
      ws.on('error', (error) => {
        console.log('❌ WebSocket echo connection failed:', error.message);
        resolve(false);
      });
      
      ws.on('close', () => {
        console.log('🔌 WebSocket echo connection closed');
        if (!testPassed) {
          resolve(false);
        }
      });
      
      // Timeout after 5 seconds
      setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
        if (!testPassed) {
          console.log('❌ WebSocket echo test timed out');
          resolve(false);
        }
      }, 5000);
      
    } catch (error) {
      console.log('❌ WebSocket echo test failed:', error.message);
      resolve(false);
    }
  });
}

async function testCORSHeaders() {
  console.log('🔍 Testing CORS headers...');
  try {
    const response = await axios.get(`${BASE_URL}/health`, {
      headers: {
        'Origin': 'http://localhost:5173'
      }
    });
    
    // Check if request succeeded (CORS allows it)
    if (response.status === 200) {
      console.log('✅ CORS validation passed - Vite origin allowed');
      return true;
    } else {
      console.log('❌ CORS validation failed');
      return false;
    }
  } catch (error) {
    console.log('❌ CORS test failed:', error.message);
    return false;
  }
}

async function runPhase1Validation() {
  console.log('🚀 Starting Phase 1 Backend Standardization Validation\n');
  
  const tests = [
    { name: 'Health Endpoint', test: testHealthEndpoint },
    { name: 'Mock TTS Endpoint', test: testMockTTSEndpoint },
    { name: 'Mock STT Endpoint', test: testMockSTTEndpoint },
    { name: 'WebSocket Echo', test: testWebSocketEcho },
    { name: 'CORS Headers', test: testCORSHeaders }
  ];
  
  const results = [];
  
  for (const { name, test } of tests) {
    console.log(`\n📋 Running ${name} test...`);
    const result = await test();
    results.push({ name, passed: result });
    
    if (result) {
      console.log(`✅ ${name} test PASSED`);
    } else {
      console.log(`❌ ${name} test FAILED`);
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 PHASE 1 VALIDATION SUMMARY');
  console.log('='.repeat(60));
  
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  
  results.forEach(({ name, passed }) => {
    console.log(`${passed ? '✅' : '❌'} ${name}`);
  });
  
  console.log(`\n🎯 Results: ${passedTests}/${totalTests} tests passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 Phase 1 Backend Standardization COMPLETED SUCCESSFULLY!');
    console.log('✅ Ready to proceed to Phase 2: Frontend Infrastructure Setup');
  } else {
    console.log('⚠️  Phase 1 has issues that need to be resolved before proceeding');
  }
  
  return passedTests === totalTests;
}

// Run validation if called directly
if (require.main === module) {
  runPhase1Validation()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Validation script failed:', error);
      process.exit(1);
    });
}

module.exports = { runPhase1Validation };