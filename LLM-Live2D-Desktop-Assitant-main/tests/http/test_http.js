/**
 * Test script for Claude HTTP API
 * 
 * This script tests the HTTP client implementation for Claude.
 * It makes a request to the Claude API and displays the response.
 */

const { askClaude } = require('../../src/main/claudeClient');
const { readConfig, saveConfig } = require('../../src/config/appConfig');

// Test message to send to Claude
const testMessage = "Hello Claude, this is a test message. Please respond with a short greeting.";

/**
 * Test the Claude API
 */
async function testClaudeAPI() {
  try {
    // Get the current config
    const config = readConfig();
    console.log(`Current HTTP base URL: ${config.httpBase || 'Not set'}`);
    
    // If HTTP base URL is not set, set a test URL
    if (!config.httpBase) {
      console.log('HTTP base URL is not set. Please set it in the Settings panel or .env file.');
      return;
    }
    
    console.log(`Sending message to Claude: "${testMessage}"`);
    
    // Send the message to Claude
    const reply = await askClaude(testMessage);
    
    console.log('Response from Claude:');
    console.log(reply);
  } catch (error) {
    console.error('Error testing Claude API:', error.message);
  }
}

// Run the test
testClaudeAPI();
