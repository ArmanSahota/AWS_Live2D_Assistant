/**
 * JavaScript wrapper for running Python TTS tests
 */

const { execSync } = require('child_process');
const path = require('path');

// Get the path to the Python test file
const testFilePath = path.join(__dirname, 'test_tts.py');

try {
  // Run the Python test file
  console.log('Running TTS tests with Python...');
  execSync(`python "${testFilePath}"`, { stdio: 'inherit' });
  console.log('TTS tests completed successfully');
} catch (error) {
  console.error(`TTS tests failed with error: ${error.message}`);
  process.exit(1);
}
