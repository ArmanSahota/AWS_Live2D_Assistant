/**
 * Direct test script for Claude HTTP API
 * 
 * This script directly tests the HTTP client implementation for Claude
 * without relying on the Electron app configuration.
 */

// Set environment variables directly
process.env.VITE_HTTP_BASE = 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev';

// Test message to send to Claude
const testMessage = "Hello Claude, this is a test message. Please respond with a short greeting.";

/**
 * Make a request to the Claude API
 * @param {string} text The text to send to Claude
 * @returns {Promise<string>} The response from Claude
 */
async function askClaude(text) {
  const httpBase = process.env.VITE_HTTP_BASE;
  
  if (!httpBase) {
    throw new Error('HTTP base URL is not configured');
  }
  
  const url = `${httpBase}/claude`;
  console.log(`Sending request to: ${url}`);
  
  try {
    // Prepare the request
    const request = { text };
    
    // Send the request
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    // Check for errors
    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}`;
      
      try {
        // Try to parse the error response as JSON
        const errorData = await response.json();
        if (errorData.error) {
          errorMessage = `HTTP error ${response.status}: ${errorData.error}`;
        }
      } catch (e) {
        // If parsing fails, use the status text
        errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      }
      
      throw new Error(errorMessage);
    }
    
    // Parse the response
    const data = await response.json();
    
    // Check if the reply is missing
    if (!data.reply) {
      throw new Error('Invalid response: missing reply field');
    }
    
    return data.reply;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

/**
 * Test the Claude API
 */
async function testClaudeAPI() {
  try {
    console.log(`HTTP base URL: ${process.env.VITE_HTTP_BASE}`);
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
