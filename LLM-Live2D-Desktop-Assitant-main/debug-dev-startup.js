#!/usr/bin/env node

/**
 * Debug Development Startup Script
 * Helps troubleshoot issues with npm run dev
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function checkDependencies() {
  console.log('🔍 Checking dependencies...');
  
  // Check root dependencies
  const rootNodeModules = fs.existsSync('node_modules');
  console.log(`${rootNodeModules ? '✅' : '❌'} Root node_modules: ${rootNodeModules}`);
  
  // Check frontend dependencies
  const frontendNodeModules = fs.existsSync('frontend/node_modules');
  console.log(`${frontendNodeModules ? '✅' : '❌'} Frontend node_modules: ${frontendNodeModules}`);
  
  // Check specific dependencies
  const requiredDeps = [
    'node_modules/concurrently',
    'node_modules/cross-env', 
    'node_modules/wait-on',
    'frontend/node_modules/vite',
    'frontend/node_modules/react'
  ];
  
  for (const dep of requiredDeps) {
    const exists = fs.existsSync(dep);
    console.log(`${exists ? '✅' : '❌'} ${dep}: ${exists}`);
  }
  
  return rootNodeModules && frontendNodeModules;
}

async function testBackendStart() {
  console.log('\n🐍 Testing backend startup...');
  
  return new Promise((resolve) => {
    const backend = spawn('python', ['server.py', '--port', '8000'], {
      stdio: 'pipe',
      cwd: process.cwd()
    });
    
    let output = '';
    
    backend.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`[Backend] ${data.toString().trim()}`);
      
      if (output.includes('Server is running')) {
        console.log('✅ Backend started successfully');
        backend.kill();
        resolve(true);
      }
    });
    
    backend.stderr.on('data', (data) => {
      console.log(`[Backend Error] ${data.toString().trim()}`);
    });
    
    backend.on('error', (error) => {
      console.log(`❌ Backend startup error: ${error.message}`);
      resolve(false);
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      console.log('⏰ Backend test timed out');
      backend.kill();
      resolve(false);
    }, 10000);
  });
}

async function testFrontendStart() {
  console.log('\n⚛️ Testing frontend startup...');
  
  return new Promise((resolve) => {
    const frontend = spawn('npm', ['run', 'dev'], {
      stdio: 'pipe',
      cwd: path.join(process.cwd(), 'frontend')
    });
    
    let output = '';
    
    frontend.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`[Frontend] ${data.toString().trim()}`);
      
      if (output.includes('Local:') && output.includes('5173')) {
        console.log('✅ Frontend started successfully');
        frontend.kill();
        resolve(true);
      }
    });
    
    frontend.stderr.on('data', (data) => {
      console.log(`[Frontend Error] ${data.toString().trim()}`);
    });
    
    frontend.on('error', (error) => {
      console.log(`❌ Frontend startup error: ${error.message}`);
      resolve(false);
    });
    
    // Timeout after 15 seconds
    setTimeout(() => {
      console.log('⏰ Frontend test timed out');
      frontend.kill();
      resolve(false);
    }, 15000);
  });
}

async function testElectronStart() {
  console.log('\n🖥️ Testing Electron startup...');
  
  return new Promise((resolve) => {
    const electron = spawn('npm', ['run', 'electron:dev'], {
      stdio: 'pipe',
      cwd: process.cwd()
    });
    
    let output = '';
    
    electron.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`[Electron] ${data.toString().trim()}`);
    });
    
    electron.stderr.on('data', (data) => {
      const errorText = data.toString().trim();
      console.log(`[Electron Error] ${errorText}`);
      
      // Check for common Electron startup issues
      if (errorText.includes('ECONNREFUSED')) {
        console.log('❌ Electron cannot connect to frontend - frontend not ready');
      } else if (errorText.includes('Error: spawn')) {
        console.log('❌ Electron spawn error - check Electron installation');
      }
    });
    
    electron.on('error', (error) => {
      console.log(`❌ Electron startup error: ${error.message}`);
      resolve(false);
    });
    
    electron.on('close', (code) => {
      console.log(`Electron process exited with code: ${code}`);
      resolve(code === 0);
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      console.log('⏰ Electron test timed out');
      electron.kill();
      resolve(false);
    }, 10000);
  });
}

async function runDebugDiagnostics() {
  console.log('🚀 Starting Development Startup Debug\n');
  
  // Check dependencies
  const depsOk = await checkDependencies();
  if (!depsOk) {
    console.log('\n❌ Dependencies missing. Run: npm run install:all');
    return false;
  }
  
  // Test backend
  const backendOk = await testBackendStart();
  if (!backendOk) {
    console.log('\n❌ Backend startup failed. Check Python and dependencies.');
    return false;
  }
  
  // Test frontend
  const frontendOk = await testFrontendStart();
  if (!frontendOk) {
    console.log('\n❌ Frontend startup failed. Check frontend dependencies.');
    return false;
  }
  
  // Test Electron
  const electronOk = await testElectronStart();
  if (!electronOk) {
    console.log('\n❌ Electron startup failed. Check Electron installation.');
    return false;
  }
  
  console.log('\n🎉 All components started successfully!');
  console.log('\n📋 Recommended startup sequence:');
  console.log('1. npm run dev:backend    # Start backend first');
  console.log('2. npm run dev:frontend   # Start frontend second');
  console.log('3. npm run electron:dev   # Start Electron last');
  console.log('\nOr use: npm run dev (starts all concurrently)');
  
  return true;
}

// Run diagnostics if called directly
if (require.main === module) {
  runDebugDiagnostics()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Debug script failed:', error);
      process.exit(1);
    });
}

module.exports = { runDebugDiagnostics };