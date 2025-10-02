/**
 * Diagnostic Validation Script
 * 
 * This script validates the identified critical issues before applying fixes.
 * Run this to confirm the root causes of the Live2D Desktop Assistant problems.
 */

const fs = require('fs');
const path = require('path');

console.log('=== LIVE2D DESKTOP ASSISTANT DIAGNOSTIC VALIDATION ===\n');

// 1. Check for IPC Handler Conflicts
console.log('1. CHECKING IPC HANDLER CONFLICTS:');
const ipcTsExists = fs.existsSync('./src/main/ipc.ts');
const ipcJsExists = fs.existsSync('./src/main/ipc.js');
const claudeTsExists = fs.existsSync('./src/main/claudeClient.ts');
const claudeJsExists = fs.existsSync('./src/main/claudeClient.js');

console.log(`   - ipc.ts exists: ${ipcTsExists}`);
console.log(`   - ipc.js exists: ${ipcJsExists}`);
console.log(`   - claudeClient.ts exists: ${claudeTsExists}`);
console.log(`   - claudeClient.js exists: ${claudeJsExists}`);

if (ipcTsExists && ipcJsExists) {
    console.log('   ⚠️  CONFLICT DETECTED: Both TypeScript and JavaScript IPC handlers exist');
}
if (claudeTsExists && claudeJsExists) {
    console.log('   ⚠️  CONFLICT DETECTED: Both TypeScript and JavaScript Claude clients exist');
}

// 2. Check Live2D Model Assets
console.log('\n2. CHECKING LIVE2D MODEL ASSETS:');
const defaultModelPath = './static/desktop/models/default';
const testModelPath = './static/desktop/models/test-model';

function checkModelAssets(modelPath, modelName) {
    console.log(`   Checking ${modelName}:`);
    const mocFile = path.join(modelPath, 'LSS.moc3');
    const textureFile = path.join(modelPath, 'LSS.4096/texture_00.png');
    const physicsFile = path.join(modelPath, 'LSS.physics3.json');
    
    console.log(`     - LSS.moc3: ${fs.existsSync(mocFile) ? '✓' : '✗'}`);
    console.log(`     - texture_00.png: ${fs.existsSync(textureFile) ? '✓' : '✗'}`);
    console.log(`     - LSS.physics3.json: ${fs.existsSync(physicsFile) ? '✓' : '✗'}`);
}

checkModelAssets(defaultModelPath, 'default model');
checkModelAssets(testModelPath, 'test model');

// 3. Check TypeScript Configuration
console.log('\n3. CHECKING TYPESCRIPT CONFIGURATION:');
try {
    const tsconfig = JSON.parse(fs.readFileSync('./tsconfig.json', 'utf8'));
    console.log('   TypeScript files in compilation:');
    tsconfig.files.forEach(file => {
        const exists = fs.existsSync(file);
        console.log(`     - ${file}: ${exists ? '✓' : '✗'}`);
        if (!exists) {
            console.log(`       ⚠️  File referenced in tsconfig.json but doesn't exist`);
        }
    });
} catch (e) {
    console.log(`   ✗ Error reading tsconfig.json: ${e.message}`);
}

// 4. Check Main.js Imports
console.log('\n4. CHECKING MAIN.JS IMPORTS:');
try {
    const mainJs = fs.readFileSync('./main.js', 'utf8');
    const ipcImportMatch = mainJs.match(/require\(['"]\.\/src\/main\/ipc\.js['"]\)/);
    const claudeImportMatch = mainJs.match(/require\(['"]\.\/src\/main\/claudeClient\.js['"]\)/);
    
    console.log(`   - Imports ipc.js: ${ipcImportMatch ? '✓' : '✗'}`);
    console.log(`   - References claudeClient: ${claudeImportMatch ? '✓' : '✗'}`);
    
    if (mainJs.includes('ipc.ts') || mainJs.includes('claudeClient.ts')) {
        console.log('   ⚠️  WARNING: main.js references TypeScript files directly');
    }
} catch (e) {
    console.log(`   ✗ Error reading main.js: ${e.message}`);
}

// 5. Check WebSocket Configuration
console.log('\n5. CHECKING WEBSOCKET CONFIGURATION:');
const websocketJs = './static/desktop/websocket.js';
if (fs.existsSync(websocketJs)) {
    const wsContent = fs.readFileSync(websocketJs, 'utf8');
    const portDiscoveryLines = wsContent.split('\n').filter(line => 
        line.includes('POSSIBLE_PORTS') || line.includes('getServerPort')
    ).length;
    console.log(`   - WebSocket port discovery complexity: ${portDiscoveryLines} relevant lines`);
    console.log(`   - Uses fallback port discovery: ${wsContent.includes('POSSIBLE_PORTS') ? '✓' : '✗'}`);
} else {
    console.log('   ✗ websocket.js not found');
}

console.log('\n=== DIAGNOSTIC COMPLETE ===');
console.log('\nRECOMMENDED ACTIONS:');
console.log('1. Remove TypeScript duplicates (ipc.ts, claudeClient.ts, models.ts)');
console.log('2. Update tsconfig.json to remove deleted files');
console.log('3. Verify Live2D model configuration points to correct assets');
console.log('4. Simplify WebSocket port discovery logic');
console.log('5. Add proper error handling to audio pipeline');