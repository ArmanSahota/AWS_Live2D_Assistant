// Debug script for speech pipeline issues
const chalk = require('chalk');

console.log(chalk.blue.bold('\n=== Speech Pipeline Debugging Script ===\n'));

// Check 1: WebSocket Connection
function checkWebSocketConnection() {
    console.log(chalk.yellow('1. Checking WebSocket Connection...'));
    
    const WebSocket = require('ws');
    const ports = [1018, 1025, 1026, 8050, 8051];
    let connected = false;
    
    return new Promise(async (resolve) => {
        for (const port of ports) {
            try {
                const ws = new WebSocket(`ws://127.0.0.1:${port}/client-ws`);
                
                await new Promise((resolveInner) => {
                    const timeout = setTimeout(() => {
                        ws.close();
                        resolveInner(false);
                    }, 1000);
                    
                    ws.on('open', () => {
                        clearTimeout(timeout);
                        console.log(chalk.green(`✓ WebSocket connected on port ${port}`));
                        connected = true;
                        ws.close();
                        resolveInner(true);
                    });
                    
                    ws.on('error', () => {
                        clearTimeout(timeout);
                        resolveInner(false);
                    });
                });
                
                if (connected) {
                    resolve(port);
                    return;
                }
            } catch (err) {
                console.log(chalk.gray(`  Port ${port}: Not available`));
            }
        }
        
        if (!connected) {
            console.log(chalk.red('✗ No WebSocket server found on any port'));
            resolve(null);
        }
    });
}

// Check 2: Configuration
async function checkConfiguration() {
    console.log(chalk.yellow('\n2. Checking Configuration...'));
    
    const yaml = require('js-yaml');
    const fs = require('fs');
    const path = require('path');
    
    try {
        const configPath = path.join(__dirname, 'conf.yaml');
        const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
        
        console.log(chalk.cyan('  Speech Configuration:'));
        console.log(`    VOICE_INPUT_ON: ${config.VOICE_INPUT_ON ? chalk.green('✓') : chalk.red('✗')}`);
        console.log(`    TTS_ON: ${config.TTS_ON ? chalk.green('✓') : chalk.red('✗')}`);
        console.log(`    ASR_MODEL: ${config.ASR_MODEL}`);
        console.log(`    TTS_MODEL: ${config.TTS_MODEL}`);
        
        if (!config.VOICE_INPUT_ON) {
            console.log(chalk.red('  ⚠ Voice input is disabled in configuration!'));
        }
        
        return config;
    } catch (error) {
        console.log(chalk.red('✗ Failed to read configuration:', error.message));
        return null;
    }
}

// Check 3: Python Dependencies
async function checkPythonDependencies() {
    console.log(chalk.yellow('\n3. Checking Python Dependencies...'));
    
    const { exec } = require('child_process');
    const util = require('util');
    const execPromise = util.promisify(exec);
    
    const dependencies = [
        { name: 'faster-whisper', check: 'python -c "import faster_whisper; print(\'OK\')"' },
        { name: 'edge-tts', check: 'python -c "import edge_tts; print(\'OK\')"' },
        { name: 'numpy', check: 'python -c "import numpy; print(\'OK\')"' },
        { name: 'soundfile', check: 'python -c "import soundfile; print(\'OK\')"' }
    ];
    
    for (const dep of dependencies) {
        try {
            const { stdout } = await execPromise(dep.check);
            if (stdout.trim() === 'OK') {
                console.log(chalk.green(`  ✓ ${dep.name} installed`));
            }
        } catch (error) {
            console.log(chalk.red(`  ✗ ${dep.name} not installed or not working`));
        }
    }
}

// Check 4: Microphone Access
async function checkMicrophoneAccess() {
    console.log(chalk.yellow('\n4. Checking Microphone Access...'));
    
    // This would need to be run in the Electron context
    console.log(chalk.gray('  Note: Microphone access must be checked in the Electron app'));
    console.log(chalk.cyan('  Ensure:'));
    console.log('    - Microphone permissions are granted');
    console.log('    - A microphone device is selected');
    console.log('    - The microphone is not being used by another app');
}

// Check 5: Test Audio Flow
async function testAudioFlow(wsPort) {
    if (!wsPort) {
        console.log(chalk.yellow('\n5. Skipping Audio Flow Test (no WebSocket connection)'));
        return;
    }
    
    console.log(chalk.yellow('\n5. Testing Audio Flow...'));
    
    const WebSocket = require('ws');
    const ws = new WebSocket(`ws://127.0.0.1:${wsPort}/client-ws`);
    
    return new Promise((resolve) => {
        ws.on('open', () => {
            console.log(chalk.green('  ✓ Connected to WebSocket'));
            
            // Send a test audio message
            const testAudio = new Float32Array(4096).fill(0);
            ws.send(JSON.stringify({
                type: 'mic-audio-data',
                audio: Array.from(testAudio),
                clipboardData: { text: '', image: null }
            }));
            
            ws.send(JSON.stringify({
                type: 'mic-audio-end',
                clipboardData: { text: '', image: null }
            }));
            
            console.log(chalk.cyan('  → Sent test audio data'));
            
            // Listen for response
            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    console.log(chalk.cyan(`  ← Received: ${message.type}`));
                    
                    if (message.type === 'transcription') {
                        console.log(chalk.green(`  ✓ STT Response: "${message.text}"`));
                    }
                } catch (error) {
                    console.log(chalk.gray('  Received non-JSON message'));
                }
            });
            
            // Close after 5 seconds
            setTimeout(() => {
                ws.close();
                resolve();
            }, 5000);
        });
        
        ws.on('error', (error) => {
            console.log(chalk.red('  ✗ WebSocket error:', error.message));
            resolve();
        });
    });
}

// Main diagnostic function
async function runDiagnostics() {
    console.log(chalk.cyan('Starting diagnostics...\n'));
    
    // Run checks
    const wsPort = await checkWebSocketConnection();
    const config = await checkConfiguration();
    await checkPythonDependencies();
    await checkMicrophoneAccess();
    await testAudioFlow(wsPort);
    
    // Summary
    console.log(chalk.blue.bold('\n=== Diagnostic Summary ===\n'));
    
    if (!wsPort) {
        console.log(chalk.red('⚠ Critical Issue: WebSocket server not running'));
        console.log(chalk.yellow('  Solution: Start the application first (npm start)'));
    }
    
    if (config && !config.VOICE_INPUT_ON) {
        console.log(chalk.red('⚠ Critical Issue: Voice input disabled'));
        console.log(chalk.yellow('  Solution: Set VOICE_INPUT_ON: true in conf.yaml'));
    }
    
    console.log(chalk.cyan('\nRecommended fixes:'));
    console.log('1. Ensure the app is running (npm start)');
    console.log('2. Check the browser console for WebSocket connection errors');
    console.log('3. Verify microphone permissions in system settings');
    console.log('4. Try speaking clearly after clicking the microphone button');
    console.log('5. Check the terminal output for Python errors');
    
    console.log(chalk.green('\n✓ Diagnostics complete!\n'));
}

// Run diagnostics
runDiagnostics().catch(console.error);