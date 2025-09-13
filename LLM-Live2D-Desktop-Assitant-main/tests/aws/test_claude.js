/**
 * Test AWS Claude API integration
 */

const { 
  assert, 
  assertEqual, 
  assertDeepEqual, 
  runTest 
} = require('../utils');

// Import the Claude client module
// Note: This assumes the Claude client is exported from the module
const { createClaudeClient } = require('../../src/main/claudeClient');

// Mock AWS SDK to avoid actual API calls
jest.mock('aws-sdk', () => {
  return {
    BedrockRuntime: jest.fn().mockImplementation(() => {
      return {
        invokeModel: jest.fn().mockImplementation(({ body }) => {
          const parsedBody = JSON.parse(body);
          return {
            promise: jest.fn().mockResolvedValue({
              body: JSON.stringify({
                completion: `This is a mock response for: ${parsedBody.prompt}`,
                stop_reason: 'stop_sequence'
              })
            })
          };
        }),
        invokeModelWithResponseStream: jest.fn().mockImplementation(({ body }) => {
          const parsedBody = JSON.parse(body);
          return {
            promise: jest.fn().mockResolvedValue({
              body: {
                on: jest.fn().mockImplementation((event, callback) => {
                  if (event === 'data') {
                    callback({
                      chunk: {
                        bytes: Buffer.from(JSON.stringify({
                          completion: `This is a mock streaming response for: ${parsedBody.prompt}`,
                          stop_reason: null
                        }))
                      }
                    });
                    callback({
                      chunk: {
                        bytes: Buffer.from(JSON.stringify({
                          completion: '',
                          stop_reason: 'stop_sequence'
                        }))
                      }
                    });
                  }
                  if (event === 'end') {
                    callback();
                  }
                  return { on: jest.fn() };
                })
              }
            })
          };
        })
      };
    })
  };
});

// Run tests
async function runTests() {
  try {
    let passed = 0;
    let total = 0;
    
    // Test Claude client creation
    total++;
    if (await runTest('Claude client creation', testClaudeClientCreation)) {
      passed++;
    }
    
    // Test Claude completion
    total++;
    if (await runTest('Claude completion', testClaudeCompletion)) {
      passed++;
    }
    
    // Test Claude streaming
    total++;
    if (await runTest('Claude streaming', testClaudeStreaming)) {
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
 * Test Claude client creation
 */
async function testClaudeClientCreation() {
  // Create a Claude client
  const claudeClient = createClaudeClient({
    region: 'us-west-2',
    model: 'anthropic.claude-v2',
    maxTokens: 1000
  });
  
  // Assert that the Claude client is not null or undefined
  assert(claudeClient !== null && claudeClient !== undefined, 'Claude client should not be null or undefined');
  
  // Assert that the Claude client has the expected methods
  assert(typeof claudeClient.complete === 'function', 'Claude client should have a complete method');
  assert(typeof claudeClient.completeStreaming === 'function', 'Claude client should have a completeStreaming method');
}

/**
 * Test Claude completion
 */
async function testClaudeCompletion() {
  // Create a Claude client
  const claudeClient = createClaudeClient({
    region: 'us-west-2',
    model: 'anthropic.claude-v2',
    maxTokens: 1000
  });
  
  // Call the complete method
  const prompt = 'Hello, Claude!';
  const response = await claudeClient.complete(prompt);
  
  // Assert that the response is as expected
  assert(response !== null && response !== undefined, 'Response should not be null or undefined');
  assert(typeof response.completion === 'string', 'Response should have a completion string');
  assert(response.completion.includes(prompt), 'Response should include the prompt');
  assert(response.stop_reason === 'stop_sequence', 'Response should have a stop_reason of stop_sequence');
}

/**
 * Test Claude streaming
 */
async function testClaudeStreaming() {
  // Create a Claude client
  const claudeClient = createClaudeClient({
    region: 'us-west-2',
    model: 'anthropic.claude-v2',
    maxTokens: 1000
  });
  
  // Call the completeStreaming method
  const prompt = 'Hello, Claude!';
  
  // Collect the streaming responses
  const chunks = [];
  await new Promise((resolve) => {
    claudeClient.completeStreaming(prompt, {
      onData: (chunk) => {
        chunks.push(chunk);
      },
      onEnd: () => {
        resolve();
      },
      onError: (error) => {
        throw error;
      }
    });
  });
  
  // Assert that the chunks are as expected
  assert(chunks.length > 0, 'Should have received at least one chunk');
  assert(chunks[0].completion.includes(prompt), 'First chunk should include the prompt');
  assert(chunks[chunks.length - 1].stop_reason === 'stop_sequence', 'Last chunk should have a stop_reason of stop_sequence');
}

// Run the tests if this file is executed directly
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests
};
