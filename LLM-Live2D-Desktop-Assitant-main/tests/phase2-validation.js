#!/usr/bin/env node

/**
 * Phase 2 Validation Script
 * Tests the frontend infrastructure setup for React + Vite migration
 */

const fs = require('fs');
const path = require('path');

function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, '..', filePath);
  const exists = fs.existsSync(fullPath);
  console.log(`${exists ? '✅' : '❌'} ${description}: ${filePath}`);
  return exists;
}

function checkDirectoryExists(dirPath, description) {
  const fullPath = path.join(__dirname, '..', dirPath);
  const exists = fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory();
  console.log(`${exists ? '✅' : '❌'} ${description}: ${dirPath}`);
  return exists;
}

function validatePackageJson(filePath, requiredFields) {
  try {
    const fullPath = path.join(__dirname, '..', filePath);
    const content = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    
    let allValid = true;
    for (const field of requiredFields) {
      const hasField = field.split('.').reduce((obj, key) => obj && obj[key], content);
      if (!hasField) {
        console.log(`❌ Missing field in ${filePath}: ${field}`);
        allValid = false;
      }
    }
    
    if (allValid) {
      console.log(`✅ Package.json validation passed: ${filePath}`);
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating ${filePath}: ${error.message}`);
    return false;
  }
}

function validateViteConfig() {
  try {
    const configPath = path.join(__dirname, '..', 'frontend/vite.config.ts');
    const content = fs.readFileSync(configPath, 'utf8');
    
    const checks = [
      { pattern: /port:\s*5173/, description: 'Frontend port 5173' },
      { pattern: /target:\s*['"]http:\/\/localhost:8000['"]/, description: 'API proxy to port 8000' },
      { pattern: /target:\s*['"]ws:\/\/localhost:8000['"]/, description: 'WebSocket proxy to port 8000' },
      { pattern: /outDir:\s*['"]\.\.\/dist-frontend['"]/, description: 'Build output directory' },
      { pattern: /@static['"]:\s*path\.resolve.*\.\.\/static/, description: 'Static assets alias' }
    ];
    
    let allValid = true;
    for (const check of checks) {
      const valid = check.pattern.test(content);
      console.log(`${valid ? '✅' : '❌'} Vite config - ${check.description}`);
      if (!valid) allValid = false;
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating Vite config: ${error.message}`);
    return false;
  }
}

function validateEnvironmentFiles() {
  const envFiles = [
    { file: 'frontend/.env.development', vars: ['VITE_API_BASE_URL=/api', 'VITE_WS_BASE_URL=/ws'] },
    { file: 'frontend/.env.production', vars: ['VITE_API_BASE_URL=http://localhost:8000', 'VITE_WS_BASE_URL=ws://localhost:8000'] }
  ];
  
  let allValid = true;
  
  for (const envFile of envFiles) {
    try {
      const fullPath = path.join(__dirname, '..', envFile.file);
      const content = fs.readFileSync(fullPath, 'utf8');
      
      let fileValid = true;
      for (const variable of envFile.vars) {
        if (!content.includes(variable)) {
          console.log(`❌ Missing variable in ${envFile.file}: ${variable}`);
          fileValid = false;
        }
      }
      
      if (fileValid) {
        console.log(`✅ Environment file valid: ${envFile.file}`);
      } else {
        allValid = false;
      }
    } catch (error) {
      console.log(`❌ Error reading ${envFile.file}: ${error.message}`);
      allValid = false;
    }
  }
  
  return allValid;
}

function validateAPIConfig() {
  try {
    const configPath = path.join(__dirname, '..', 'frontend/src/config/api.ts');
    const content = fs.readFileSync(configPath, 'utf8');
    
    const checks = [
      { pattern: /API_CONFIG/, description: 'API_CONFIG object' },
      { pattern: /ENDPOINTS/, description: 'ENDPOINTS object' },
      { pattern: /WS_MESSAGE_TYPES/, description: 'WS_MESSAGE_TYPES object' },
      { pattern: /getEndpointURL/, description: 'getEndpointURL function' },
      { pattern: /getWebSocketURL/, description: 'getWebSocketURL function' }
    ];
    
    let allValid = true;
    for (const check of checks) {
      const valid = check.pattern.test(content);
      console.log(`${valid ? '✅' : '❌'} API config - ${check.description}`);
      if (!valid) allValid = false;
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating API config: ${error.message}`);
    return false;
  }
}

async function runPhase2Validation() {
  console.log('🚀 Starting Phase 2 Frontend Infrastructure Validation\n');
  
  const results = [];
  
  // Directory structure validation
  console.log('📁 Validating directory structure...');
  const directories = [
    'frontend',
    'frontend/src',
    'frontend/src/components',
    'frontend/src/components/Live2D',
    'frontend/src/components/Audio',
    'frontend/src/components/WebSocket',
    'frontend/src/components/Diagnostics',
    'frontend/src/hooks',
    'frontend/src/services',
    'frontend/src/types',
    'frontend/src/config',
    'frontend/src/utils',
    'frontend/public'
  ];
  
  let directoriesValid = true;
  for (const dir of directories) {
    if (!checkDirectoryExists(dir, 'Directory')) {
      directoriesValid = false;
    }
  }
  results.push({ name: 'Directory Structure', passed: directoriesValid });
  
  // Configuration files validation
  console.log('\n📄 Validating configuration files...');
  const configFiles = [
    'frontend/package.json',
    'frontend/vite.config.ts',
    'frontend/tsconfig.json',
    'frontend/tsconfig.node.json',
    'frontend/.env.development',
    'frontend/.env.production'
  ];
  
  let configFilesValid = true;
  for (const file of configFiles) {
    if (!checkFileExists(file, 'Config file')) {
      configFilesValid = false;
    }
  }
  results.push({ name: 'Configuration Files', passed: configFilesValid });
  
  // React app files validation
  console.log('\n⚛️ Validating React app files...');
  const reactFiles = [
    'frontend/public/index.html',
    'frontend/src/main.tsx',
    'frontend/src/App.tsx',
    'frontend/src/App.css',
    'frontend/src/index.css',
    'frontend/src/vite-env.d.ts',
    'frontend/src/config/api.ts'
  ];
  
  let reactFilesValid = true;
  for (const file of reactFiles) {
    if (!checkFileExists(file, 'React file')) {
      reactFilesValid = false;
    }
  }
  results.push({ name: 'React App Files', passed: reactFilesValid });
  
  // Component files validation
  console.log('\n🧩 Validating React components...');
  const componentFiles = [
    'frontend/src/components/Live2D/Live2DViewer.tsx',
    'frontend/src/components/Audio/AudioManager.tsx',
    'frontend/src/components/WebSocket/WebSocketClient.tsx',
    'frontend/src/components/Diagnostics/DiagnosticsPanel.tsx'
  ];
  
  let componentsValid = true;
  for (const file of componentFiles) {
    if (!checkFileExists(file, 'Component')) {
      componentsValid = false;
    }
  }
  results.push({ name: 'React Components', passed: componentsValid });
  
  // Package.json validation
  console.log('\n📦 Validating package configurations...');
  const rootPackageValid = validatePackageJson('package.json', [
    'scripts.dev',
    'scripts.dev:frontend',
    'scripts.dev:backend',
    'scripts.build:frontend',
    'devDependencies.concurrently',
    'devDependencies.cross-env',
    'devDependencies.wait-on'
  ]);
  results.push({ name: 'Root Package.json', passed: rootPackageValid });
  
  const frontendPackageValid = validatePackageJson('frontend/package.json', [
    'dependencies.react',
    'dependencies.react-dom',
    'devDependencies.vite',
    'devDependencies.@vitejs/plugin-react',
    'devDependencies.typescript'
  ]);
  results.push({ name: 'Frontend Package.json', passed: frontendPackageValid });
  
  // Vite configuration validation
  console.log('\n⚡ Validating Vite configuration...');
  const viteConfigValid = validateViteConfig();
  results.push({ name: 'Vite Configuration', passed: viteConfigValid });
  
  // Environment files validation
  console.log('\n🌍 Validating environment configuration...');
  const envFilesValid = validateEnvironmentFiles();
  results.push({ name: 'Environment Files', passed: envFilesValid });
  
  // API configuration validation
  console.log('\n🔗 Validating API configuration...');
  const apiConfigValid = validateAPIConfig();
  results.push({ name: 'API Configuration', passed: apiConfigValid });
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 PHASE 2 VALIDATION SUMMARY');
  console.log('='.repeat(60));
  
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  
  results.forEach(({ name, passed }) => {
    console.log(`${passed ? '✅' : '❌'} ${name}`);
  });
  
  console.log(`\n🎯 Results: ${passedTests}/${totalTests} validations passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 Phase 2 Frontend Infrastructure Setup COMPLETED SUCCESSFULLY!');
    console.log('✅ Ready to install dependencies and test the setup');
    console.log('\n📋 Next steps:');
    console.log('1. Run: npm run install:all');
    console.log('2. Run: npm run dev');
    console.log('3. Open: http://localhost:5173');
  } else {
    console.log('⚠️  Phase 2 has issues that need to be resolved before proceeding');
  }
  
  return passedTests === totalTests;
}

// Run validation if called directly
if (require.main === module) {
  runPhase2Validation()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Validation script failed:', error);
      process.exit(1);
    });
}

module.exports = { runPhase2Validation };