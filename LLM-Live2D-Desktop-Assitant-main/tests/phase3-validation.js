#!/usr/bin/env node

/**
 * Phase 3 Validation Script
 * Tests the component migration for React + Vite migration
 */

const fs = require('fs');
const path = require('path');

function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, '..', filePath);
  const exists = fs.existsSync(fullPath);
  console.log(`${exists ? '✅' : '❌'} ${description}: ${filePath}`);
  return exists;
}

function validateHookImplementation(filePath, requiredExports) {
  try {
    const fullPath = path.join(__dirname, '..', filePath);
    const content = fs.readFileSync(fullPath, 'utf8');
    
    let allValid = true;
    for (const exportName of requiredExports) {
      const hasExport = content.includes(`export const ${exportName}`) || 
                       content.includes(`export { ${exportName}`) ||
                       content.includes(`export function ${exportName}`);
      if (!hasExport) {
        console.log(`❌ Missing export in ${filePath}: ${exportName}`);
        allValid = false;
      }
    }
    
    if (allValid) {
      console.log(`✅ Hook validation passed: ${filePath}`);
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating ${filePath}: ${error.message}`);
    return false;
  }
}

function validateComponentImplementation(filePath, requiredFeatures) {
  try {
    const fullPath = path.join(__dirname, '..', filePath);
    const content = fs.readFileSync(fullPath, 'utf8');
    
    let allValid = true;
    for (const feature of requiredFeatures) {
      const hasFeature = content.includes(feature);
      if (!hasFeature) {
        console.log(`❌ Missing feature in ${filePath}: ${feature}`);
        allValid = false;
      }
    }
    
    if (allValid) {
      console.log(`✅ Component validation passed: ${filePath}`);
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating ${filePath}: ${error.message}`);
    return false;
  }
}

async function runPhase3Validation() {
  console.log('🚀 Starting Phase 3 Component Migration Validation\n');
  
  const results = [];
  
  // Hook implementations validation
  console.log('🪝 Validating React hooks...');
  
  const hookValidations = [
    {
      name: 'useWebSocket Hook',
      file: 'frontend/src/hooks/useWebSocket.ts',
      exports: ['useWebSocket']
    },
    {
      name: 'useAPI Hook',
      file: 'frontend/src/hooks/useAPI.ts',
      exports: ['useAPI', 'useHealthCheck', 'useMockTTS', 'useMockSTT']
    },
    {
      name: 'useLive2D Hook',
      file: 'frontend/src/hooks/useLive2D.ts',
      exports: ['useLive2D']
    },
    {
      name: 'useAudio Hook',
      file: 'frontend/src/hooks/useAudio.ts',
      exports: ['useAudio']
    }
  ];
  
  let hooksValid = true;
  for (const validation of hookValidations) {
    if (!validateHookImplementation(validation.file, validation.exports)) {
      hooksValid = false;
    }
  }
  results.push({ name: 'React Hooks', passed: hooksValid });
  
  // Component implementations validation
  console.log('\n🧩 Validating React components...');
  
  const componentValidations = [
    {
      name: 'WebSocketClient Component',
      file: 'frontend/src/components/WebSocket/WebSocketClient.tsx',
      features: ['useWebSocket', 'WS_MESSAGE_TYPES', 'handleWebSocketMessage']
    },
    {
      name: 'Live2DViewer Component',
      file: 'frontend/src/components/Live2D/Live2DViewer.tsx',
      features: ['useLive2D', 'canvasRef', 'loadModel']
    },
    {
      name: 'AudioManager Component',
      file: 'frontend/src/components/Audio/AudioManager.tsx',
      features: ['useAudio', 'addAudioTask', 'isPlaying']
    },
    {
      name: 'DiagnosticsPanel Component',
      file: 'frontend/src/components/Diagnostics/DiagnosticsPanel.tsx',
      features: ['useHealthCheck', 'useMockTTS', 'useMockSTT', 'useWebSocket']
    }
  ];
  
  let componentsValid = true;
  for (const validation of componentValidations) {
    if (!validateComponentImplementation(validation.file, validation.features)) {
      componentsValid = false;
    }
  }
  results.push({ name: 'React Components', passed: componentsValid });
  
  // Integration features validation
  console.log('\n🔗 Validating integration features...');
  
  const integrationChecks = [
    {
      name: 'WebSocket Integration',
      file: 'frontend/src/components/WebSocket/WebSocketClient.tsx',
      features: ['sendWebSocketMessage', 'reconnectWebSocket', 'isWebSocketConnected']
    },
    {
      name: 'Live2D Integration',
      file: 'frontend/src/components/Live2D/Live2DViewer.tsx',
      features: ['playLive2DMotion', 'setLive2DExpression', 'clearLive2DModel']
    },
    {
      name: 'Audio Integration',
      file: 'frontend/src/components/Audio/AudioManager.tsx',
      features: ['window.state', 'audioTaskQueue', 'addAudioTask']
    }
  ];
  
  let integrationValid = true;
  for (const check of integrationChecks) {
    if (!validateComponentImplementation(check.file, check.features)) {
      integrationValid = false;
    }
  }
  results.push({ name: 'Backward Compatibility', passed: integrationValid });
  
  // Hook functionality validation
  console.log('\n⚡ Validating hook functionality...');
  
  const hookFeatures = [
    {
      name: 'WebSocket Hook Features',
      file: 'frontend/src/hooks/useWebSocket.ts',
      features: ['isConnected', 'sendMessage', 'reconnect', 'autoConnect']
    },
    {
      name: 'API Hook Features',
      file: 'frontend/src/hooks/useAPI.ts',
      features: ['loading', 'error', 'data', 'get', 'post']
    },
    {
      name: 'Live2D Hook Features',
      file: 'frontend/src/hooks/useLive2D.ts',
      features: ['loadModel', 'clearModel', 'playMotion', 'setExpression']
    },
    {
      name: 'Audio Hook Features',
      file: 'frontend/src/hooks/useAudio.ts',
      features: ['addAudioTask', 'isPlaying', 'startRecording', 'stopRecording']
    }
  ];
  
  let hookFeaturesValid = true;
  for (const feature of hookFeatures) {
    if (!validateComponentImplementation(feature.file, feature.features)) {
      hookFeaturesValid = false;
    }
  }
  results.push({ name: 'Hook Functionality', passed: hookFeaturesValid });
  
  // TypeScript interfaces validation
  console.log('\n📝 Validating TypeScript interfaces...');
  
  const interfaceChecks = [
    {
      name: 'WebSocket Interfaces',
      file: 'frontend/src/hooks/useWebSocket.ts',
      features: ['WebSocketMessage', 'UseWebSocketOptions', 'UseWebSocketReturn']
    },
    {
      name: 'API Interfaces',
      file: 'frontend/src/hooks/useAPI.ts',
      features: ['APIResponse', 'UseAPIOptions']
    },
    {
      name: 'Live2D Interfaces',
      file: 'frontend/src/hooks/useLive2D.ts',
      features: ['Live2DModelInfo', 'UseLive2DOptions', 'UseLive2DReturn']
    },
    {
      name: 'Audio Interfaces',
      file: 'frontend/src/hooks/useAudio.ts',
      features: ['AudioTask', 'UseAudioOptions', 'UseAudioReturn']
    }
  ];
  
  let interfacesValid = true;
  for (const check of interfaceChecks) {
    if (!validateComponentImplementation(check.file, check.features)) {
      interfacesValid = false;
    }
  }
  results.push({ name: 'TypeScript Interfaces', passed: interfacesValid });
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 PHASE 3 VALIDATION SUMMARY');
  console.log('='.repeat(60));
  
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  
  results.forEach(({ name, passed }) => {
    console.log(`${passed ? '✅' : '❌'} ${name}`);
  });
  
  console.log(`\n🎯 Results: ${passedTests}/${totalTests} validations passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 Phase 3 Component Migration COMPLETED SUCCESSFULLY!');
    console.log('✅ All core functionality migrated to React hooks and components');
    console.log('\n📋 Next steps:');
    console.log('1. Install dependencies: npm run install:all');
    console.log('2. Test full integration: npm run dev');
    console.log('3. Validate in browser: http://localhost:5173');
    console.log('4. Test diagnostics panel functionality');
    console.log('5. Proceed to Phase 4: Electron Integration Updates');
  } else {
    console.log('⚠️  Phase 3 has issues that need to be resolved before proceeding');
  }
  
  return passedTests === totalTests;
}

// Run validation if called directly
if (require.main === module) {
  runPhase3Validation()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Validation script failed:', error);
      process.exit(1);
    });
}

module.exports = { runPhase3Validation };