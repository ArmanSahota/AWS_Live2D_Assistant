// Quick fix for missing resolveModel3Path function
// Add this to src/main/ipc.js before line 253

const path = require('path');
const fs = require('fs');
const { app } = require('electron');

/**
 * Resolve model path - finds the actual location of Live2D model files
 * @param {string} modelPath - Path to the model file
 * @returns {string} - Resolved full path
 */
function resolveModel3Path(modelPath) {
    // If path already exists, return it
    if (fs.existsSync(modelPath)) {
        return modelPath;
    }
    
    // Get base path depending on if app is packaged
    const basePath = app.isPackaged 
        ? process.resourcesPath 
        : path.join(__dirname, '..', '..');
    
    // Try different possible locations
    const possiblePaths = [
        modelPath,
        path.join(basePath, modelPath),
        path.join(basePath, 'static', 'desktop', 'models', modelPath),
        path.join(basePath, 'static', 'desktop', modelPath),
        path.join(__dirname, '..', '..', 'static', 'desktop', 'models', modelPath)
    ];
    
    // Check each possible path
    for (const p of possiblePaths) {
        if (fs.existsSync(p)) {
            console.log(`Model found at: ${p}`);
            return p;
        }
    }
    
    // If not found, log warning and return original path
    console.warn(`Model path not found: ${modelPath}`);
    console.warn(`Searched in: ${possiblePaths.join(', ')}`);
    
    // Return the original path anyway (might work with relative paths)
    return modelPath;
}

// Export for use in ipc.js
module.exports = { resolveModel3Path };