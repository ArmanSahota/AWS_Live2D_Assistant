/**
 * Test runner for the LLM-Live2D-Desktop-Assistant
 * 
 * This file provides a centralized way to run tests for different components
 * of the application. It helps organize tests by category and provides
 * a simple interface to run them.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Test categories
const TEST_CATEGORIES = {
  AWS: 'aws',
  HTTP: 'http',
  WS: 'ws',
  CONFIG: 'config',
  ELECTRON: 'electron',
  TTS: 'tts'
};

// Get command line arguments
const args = process.argv.slice(2);
const category = args[0];
const specificTest = args[1];

/**
 * Run tests based on category and specific test name
 * @param {string} category - Test category
 * @param {string} specificTest - Specific test to run (optional)
 */
function runTests(category, specificTest) {
  if (!category) {
    console.log('Available test categories:');
    Object.values(TEST_CATEGORIES).forEach(cat => {
      console.log(`- ${cat}`);
    });
    console.log('\nUsage: node tests/index.js [category] [specific-test]');
    return;
  }

  const categoryPath = path.join(__dirname, category);
  
  if (!fs.existsSync(categoryPath)) {
    console.error(`Error: Test category '${category}' not found.`);
    return;
  }

  if (specificTest) {
    const testPath = path.join(categoryPath, `${specificTest}.js`);
    if (!fs.existsSync(testPath)) {
      console.error(`Error: Test '${specificTest}' not found in category '${category}'.`);
      return;
    }
    
    console.log(`Running test: ${category}/${specificTest}`);
    try {
      execSync(`node ${testPath}`, { stdio: 'inherit' });
    } catch (error) {
      console.error(`Test failed with error: ${error.message}`);
      process.exit(1);
    }
  } else {
    // Run all tests in the category
    console.log(`Running all tests in category: ${category}`);
    
    const files = fs.readdirSync(categoryPath)
      .filter(file => file.endsWith('.js'));
    
    if (files.length === 0) {
      console.log(`No tests found in category '${category}'.`);
      return;
    }
    
    let failedTests = 0;
    
    files.forEach(file => {
      const testPath = path.join(categoryPath, file);
      console.log(`\nRunning test: ${file}`);
      try {
        execSync(`node ${testPath}`, { stdio: 'inherit' });
        console.log(`✓ Test ${file} passed`);
      } catch (error) {
        console.error(`✗ Test ${file} failed with error: ${error.message}`);
        failedTests++;
      }
    });
    
    console.log(`\nTest summary: ${files.length - failedTests}/${files.length} tests passed`);
    
    if (failedTests > 0) {
      process.exit(1);
    }
  }
}

// Run the tests
runTests(category, specificTest);
