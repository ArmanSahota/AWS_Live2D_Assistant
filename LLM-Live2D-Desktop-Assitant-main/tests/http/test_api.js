/**
 * Test HTTP API functionality
 */

const http = require('http');
const { promisify } = require('util');
const { 
  assert, 
  assertEqual, 
  assertDeepEqual, 
  runTest 
} = require('../utils');

// Import the mock API module
const { createApiClient } = require('./api');

// Run tests
async function runTests() {
  try {
    let passed = 0;
    let total = 0;
    
    // Test API client creation
    total++;
    if (await runTest('API client creation', testApiClientCreation)) {
      passed++;
    }
    
    // Test API request
    total++;
    if (await runTest('API request', testApiRequest)) {
      passed++;
    }
    
    // Test API error handling
    total++;
    if (await runTest('API error handling', testApiErrorHandling)) {
      passed++;
    }
    
    console.log(`\nTest summary: ${passed}/${total} tests passed`);
    
    if (passed < total) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

/**
 * Test API client creation
 */
async function testApiClientCreation() {
  // Create an API client
  const apiClient = createApiClient({
    baseUrl: 'http://localhost:8000',  // Keep 8000 as standard
    timeout: 5000
  });
  
  // Assert that the API client is not null or undefined
  assert(apiClient !== null && apiClient !== undefined, 'API client should not be null or undefined');
  
  // Assert that the API client has the expected methods
  assert(typeof apiClient.get === 'function', 'API client should have a get method');
  assert(typeof apiClient.post === 'function', 'API client should have a post method');
  assert(typeof apiClient.put === 'function', 'API client should have a put method');
  assert(typeof apiClient.delete === 'function', 'API client should have a delete method');
}

/**
 * Test API request
 */
async function testApiRequest() {
  // Create a mock server
  const server = http.createServer((req, res) => {
    if (req.url === '/test' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ message: 'Test successful' }));
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  
  // Start the server
  await promisify(server.listen.bind(server))(0);
  const port = server.address().port;
  
  try {
    // Create an API client
    const apiClient = createApiClient({
      baseUrl: `http://localhost:${port}`,
      timeout: 1000
    });
    
    // Make a request
    const response = await apiClient.get('/test');
    
    // Assert that the response is as expected
    assertEqual(response.status, 200, 'Response status should be 200');
    assertDeepEqual(response.data, { message: 'Test successful' }, 'Response data should match expected data');
  } finally {
    // Close the server
    await promisify(server.close.bind(server))();
  }
}

/**
 * Test API error handling
 */
async function testApiErrorHandling() {
  // Create a mock server
  const server = http.createServer((req, res) => {
    if (req.url === '/error' && req.method === 'GET') {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Internal server error' }));
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  
  // Start the server
  await promisify(server.listen.bind(server))(0);
  const port = server.address().port;
  
  try {
    // Create an API client
    const apiClient = createApiClient({
      baseUrl: `http://localhost:${port}`,
      timeout: 1000
    });
    
    try {
      // Make a request that should fail
      await apiClient.get('/error');
      
      // If we get here, the test failed
      throw new Error('API request should have thrown an error');
    } catch (error) {
      // The test passed if an error was thrown
      assert(error instanceof Error, 'Error should be an instance of Error');
      assertEqual(error.response?.status, 500, 'Error response status should be 500');
      assertDeepEqual(error.response?.data, { error: 'Internal server error' }, 'Error response data should match expected data');
    }
  } finally {
    // Close the server
    await promisify(server.close.bind(server))();
  }
}

// Run the tests if this file is executed directly
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests
};
