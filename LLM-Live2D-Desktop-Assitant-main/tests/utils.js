/**
 * Utility functions for tests
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const access = promisify(fs.access);

/**
 * Check if a file exists
 * @param {string} filePath - Path to the file
 * @returns {Promise<boolean>} - True if the file exists, false otherwise
 */
async function fileExists(filePath) {
  try {
    await access(filePath, fs.constants.F_OK);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Create a directory if it doesn't exist
 * @param {string} dirPath - Path to the directory
 * @returns {Promise<void>}
 */
async function ensureDir(dirPath) {
  if (!(await fileExists(dirPath))) {
    await mkdir(dirPath, { recursive: true });
  }
}

/**
 * Read a JSON file
 * @param {string} filePath - Path to the JSON file
 * @returns {Promise<object>} - Parsed JSON object
 */
async function readJsonFile(filePath) {
  const content = await readFile(filePath, 'utf8');
  return JSON.parse(content);
}

/**
 * Write a JSON file
 * @param {string} filePath - Path to the JSON file
 * @param {object} data - Data to write
 * @returns {Promise<void>}
 */
async function writeJsonFile(filePath, data) {
  await ensureDir(path.dirname(filePath));
  await writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
}

/**
 * Create a temporary test file
 * @param {string} content - Content to write to the file
 * @param {string} [extension='.json'] - File extension
 * @returns {Promise<string>} - Path to the created file
 */
async function createTempFile(content, extension = '.json') {
  const tempDir = path.join(__dirname, 'temp');
  await ensureDir(tempDir);
  
  const fileName = `test-${Date.now()}${extension}`;
  const filePath = path.join(tempDir, fileName);
  
  await writeFile(filePath, content, 'utf8');
  return filePath;
}

/**
 * Clean up temporary test files
 * @returns {Promise<void>}
 */
async function cleanupTempFiles() {
  const tempDir = path.join(__dirname, 'temp');
  if (await fileExists(tempDir)) {
    const files = fs.readdirSync(tempDir);
    for (const file of files) {
      fs.unlinkSync(path.join(tempDir, file));
    }
  }
}

/**
 * Assert that a condition is true
 * @param {boolean} condition - Condition to check
 * @param {string} message - Error message if the condition is false
 */
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

/**
 * Assert that two values are equal
 * @param {any} actual - Actual value
 * @param {any} expected - Expected value
 * @param {string} message - Error message if the values are not equal
 */
function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(
      message || `Expected ${expected} but got ${actual}`
    );
  }
}

/**
 * Assert that two objects are deeply equal
 * @param {object} actual - Actual object
 * @param {object} expected - Expected object
 * @param {string} message - Error message if the objects are not equal
 */
function assertDeepEqual(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  
  if (actualStr !== expectedStr) {
    throw new Error(
      message || `Expected ${expectedStr} but got ${actualStr}`
    );
  }
}

/**
 * Run a test function and handle errors
 * @param {string} name - Test name
 * @param {Function} testFn - Test function
 * @returns {Promise<boolean>} - True if the test passed, false otherwise
 */
async function runTest(name, testFn) {
  console.log(`Running test: ${name}`);
  try {
    await testFn();
    console.log(`✓ Test passed: ${name}`);
    return true;
  } catch (error) {
    console.error(`✗ Test failed: ${name}`);
    console.error(`  Error: ${error.message}`);
    return false;
  }
}

module.exports = {
  fileExists,
  ensureDir,
  readJsonFile,
  writeJsonFile,
  createTempFile,
  cleanupTempFiles,
  assert,
  assertEqual,
  assertDeepEqual,
  runTest
};
