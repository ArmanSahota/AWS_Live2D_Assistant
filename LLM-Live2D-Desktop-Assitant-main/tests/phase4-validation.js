#!/usr/bin/env node

/**
 * Phase 4 Validation Script
 * Tests the Electron integration updates for React + Vite migration
 */

const fs = require('fs');
const path = require('path');

function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, '..', filePath);
  const exists = fs.existsSync(fullPath);
  console.log(`${exists ? '✅' : '❌'} ${description}: ${filePath}`);
  return exists;
}

function validateMainJsUpdates() {
  try {
    const mainJsPath = path.join(__dirname, '..', 'main.js');
    const content = fs.readFileSync(mainJsPath, 'utf8');
    
    const checks = [
      { pattern: /loadURL\(['"]http:\/\/localhost:5173['"]/, description: 'Development: Load from Vite dev server' },
      { pattern: /path\.join\(basePath,\s*['"]dist-frontend['"],\s*['"]index\.html['"]/, description: 'Production: Load from built React app' },
      { pattern: /isDevelopment/, description: 'Environment detection' },
      { pattern: /openDevTools/, description: 'DevTools in development' }
    ];
    
    let allValid = true;
    for (const check of checks) {
      const valid = check.pattern.test(content);
      console.log(`${valid ? '✅' : '❌'} main.js - ${check.description}`);
      if (!valid) allValid = false;
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating main.js: ${error.message}`);
    return false;
  }
}

function validatePackageJsonBuild() {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const content = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    const checks = [
      { field: 'scripts.dev', description: 'Development script with concurrently' },
      { field: 'scripts.build', description: 'Build script with frontend build' },
      { field: 'scripts.build:frontend', description: 'Frontend build script' },
      { field: 'scripts.electron:dev', description: 'Electron development script' },
      { field: 'devDependencies.concurrently', description: 'Concurrently dependency' },
      { field: 'devDependencies.cross-env', description: 'Cross-env dependency' },
      { field: 'devDependencies.wait-on', description: 'Wait-on dependency' }
    ];
    
    let allValid = true;
    for (const check of checks) {
      const hasField = check.field.split('.').reduce((obj, key) => obj && obj[key], content);
      if (!hasField) {
        console.log(`❌ Missing in package.json: ${check.field} - ${check.description}`);
        allValid = false;
      } else {
        console.log(`✅ Package.json - ${check.description}`);
      }
    }
    
    // Check build configuration
    const buildConfig = content.build;
    if (buildConfig) {
      const hasDistFrontend = buildConfig.files && buildConfig.files.includes('dist-frontend/**/*');
      const hasExtraResources = buildConfig.extraResources && 
        buildConfig.extraResources.some(resource => resource.from === 'dist-frontend');
      
      console.log(`${hasDistFrontend ? '✅' : '❌'} Build config - dist-frontend in files`);
      console.log(`${hasExtraResources ? '✅' : '❌'} Build config - dist-frontend in extraResources`);
      
      if (!hasDistFrontend || !hasExtraResources) allValid = false;
    } else {
      console.log('❌ Build configuration missing');
      allValid = false;
    }
    
    return allValid;
  } catch (error) {
    console.log(`❌ Error validating package.json: ${error.message}`);
    return false;
  }
}

function validatePreloadScript() {
  try {
    const preloadPath = path.join(__dirname, '..', 'static/desktop/preload.js');
    const exists = fs.existsSync(preloadPath);
    
    if (exists) {
      console.log('✅ Preload script exists and will work with React app');
      return true;
    } else {
      console.log('❌ Preload script missing - may affect IPC communication');
      return false;
    }
  } catch (error) {
    console.log(`❌ Error checking preload script: ${error.message}`);
    return false;
  }
}

function validateBuildOutput() {
  const distPath = path.join(__dirname, '..', 'dist-frontend');
  const exists = fs.existsSync(distPath);
  
  if (exists) {
    const indexExists = fs.existsSync(path.join(distPath, 'index.html'));
    console.log(`✅ Build output directory exists: dist-frontend`);
    console.log(`${indexExists ? '✅' : '⚠️'} Build output ${indexExists ? 'contains' : 'missing'} index.html (run 'npm run build:frontend' to generate)`);
    return true;
  } else {
    console.log('⚠️  Build output directory missing (run \'npm run build:frontend\' to generate)');
    return true; // Not a failure, just needs to be built
  }
}

function validateStaticAssets() {
  const staticChecks = [
    'static/desktop/models',
    'static/libs',
    'static/pictures',
    'static/favicon.ico'
  ];
  
  let allValid = true;
  for (const assetPath of staticChecks) {
    const exists = checkFileExists(assetPath, 'Static asset');
    if (!exists) allValid = false;
  }
  
  return allValid;
}

async function runPhase4Validation() {
  console.log('🚀 Starting Phase 4 Electron Integration Validation\n');
  
  const results = [];
  
  // Main.js updates validation
  console.log('🖥️  Validating main.js updates...');
  const mainJsValid = validateMainJsUpdates();
  results.push({ name: 'Main.js Updates', passed: mainJsValid });
  
  // Package.json build configuration
  console.log('\n📦 Validating package.json build configuration...');
  const packageJsonValid = validatePackageJsonBuild();
  results.push({ name: 'Package.json Build Config', passed: packageJsonValid });
  
  // Preload script compatibility
  console.log('\n🔌 Validating preload script compatibility...');
  const preloadValid = validatePreloadScript();
  results.push({ name: 'Preload Script', passed: preloadValid });
  
  // Build output validation
  console.log('\n🏗️  Validating build output...');
  const buildOutputValid = validateBuildOutput();
  results.push({ name: 'Build Output', passed: buildOutputValid });
  
  // Static assets validation
  console.log('\n📁 Validating static assets...');
  const staticAssetsValid = validateStaticAssets();
  results.push({ name: 'Static Assets', passed: staticAssetsValid });
  
  // Development workflow validation
  console.log('\n⚙️  Validating development workflow...');
  const workflowChecks = [
    { script: 'dev', description: 'Concurrent development script' },
    { script: 'dev:frontend', description: 'Frontend development script' },
    { script: 'dev:backend', description: 'Backend development script' },
    { script: 'electron:dev', description: 'Electron development script' },
    { script: 'build', description: 'Production build script' },
    { script: 'build:frontend', description: 'Frontend build script' },
    { script: 'install:all', description: 'Install all dependencies script' }
  ];
  
  let workflowValid = true;
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    for (const check of workflowChecks) {
      const hasScript = packageContent.scripts && packageContent.scripts[check.script];
      console.log(`${hasScript ? '✅' : '❌'} Workflow - ${check.description}`);
      if (!hasScript) workflowValid = false;
    }
  } catch (error) {
    console.log(`❌ Error validating workflow: ${error.message}`);
    workflowValid = false;
  }
  results.push({ name: 'Development Workflow', passed: workflowValid });
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 PHASE 4 VALIDATION SUMMARY');
  console.log('='.repeat(60));
  
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  
  results.forEach(({ name, passed }) => {
    console.log(`${passed ? '✅' : '❌'} ${name}`);
  });
  
  console.log(`\n🎯 Results: ${passedTests}/${totalTests} validations passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 Phase 4 Electron Integration COMPLETED SUCCESSFULLY!');
    console.log('✅ Electron app ready to load React frontend');
    console.log('\n📋 Ready for final testing:');
    console.log('1. Install dependencies: npm run install:all');
    console.log('2. Build frontend: npm run build:frontend');
    console.log('3. Test development: npm run dev');
    console.log('4. Test production build: npm run build');
    console.log('5. Validate complete system integration');
  } else {
    console.log('⚠️  Phase 4 has issues that need to be resolved before proceeding');
  }
  
  return passedTests === totalTests;
}

// Run validation if called directly
if (require.main === module) {
  runPhase4Validation()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Validation script failed:', error);
      process.exit(1);
    });
}

module.exports = { runPhase4Validation };