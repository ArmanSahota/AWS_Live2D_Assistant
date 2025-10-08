/**
 * RAG-Enhanced Claude HTTP Client Module
 * 
 * This module extends the basic Claude client with RAG (Retrieval-Augmented Generation)
 * capabilities, providing additional context from S3 documents without changing
 * Claude's core prompting behavior.
 */

const { readConfig } = require('../config/appConfig');
const { spawn } = require('child_process');
const path = require('path');

// Cache for the last Claude response
let lastResponse = null;

// Request queue to prevent multiple simultaneous requests
const requestQueue = [];
let isProcessing = false;

// RAG system cache
let ragSystemReady = false;
let ragSystemError = null;

/**
 * Initialize the RAG system by checking if Python dependencies are available
 */
async function initializeRAGSystem() {
  if (ragSystemReady) return true;
  
  try {
    console.log('[RAG] Initializing RAG system...');
    
    // Test if the RAG system is available by running a quick test
    const ragTestResult = await runPythonRAGQuery('test connection', true);
    
    if (ragTestResult && ragTestResult.success) {
      ragSystemReady = true;
      console.log('[RAG] ✅ RAG system initialized successfully');
      return true;
    } else {
      ragSystemError = 'RAG system test failed';
      console.log('[RAG] ❌ RAG system initialization failed');
      return false;
    }
  } catch (error) {
    ragSystemError = error.message;
    console.log(`[RAG] ❌ RAG system initialization error: ${error.message}`);
    return false;
  }
}

/**
 * Run a Python RAG query using the SimpleS3RAG system
 * @param {string} query The query to search for
 * @param {boolean} isTest Whether this is a test query
 * @returns {Promise<Object>} RAG query result
 */
function runPythonRAGQuery(query, isTest = false) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '..', '..', 'simple_s3_rag.py');
    
    // Create a simple Python script call
    const pythonProcess = spawn('python', ['-c', `
import sys
sys.path.append('${path.dirname(pythonScript)}')
from simple_s3_rag import SimpleS3RAG

try:
    rag = SimpleS3RAG()
    if "${isTest}".lower() == "true":
        # Test query - just check if we can initialize
        rag.load_documents_from_s3()
        print('{"success": true, "context": "", "message": "RAG system ready"}')
    else:
        # Real query
        relevant_chunks = rag.retrieve_relevant_chunks("${query.replace(/"/g, '\\"')}", max_chunks=2)
        if relevant_chunks:
            context_parts = []
            for chunk in relevant_chunks:
                source_name = chunk.source.split('/')[-1].replace('.txt', '').replace('-', ' ').title()
                context_parts.append(f"From {source_name}: {chunk.content[:300]}...")
            
            context = "\\n\\n".join(context_parts)
            print(f'{{"success": true, "context": "{context.replace('"', '\\"')}", "chunks_found": {len(relevant_chunks)}}}')
        else:
            print('{"success": true, "context": "", "chunks_found": 0}')
except Exception as e:
    print(f'{{"success": false, "error": "{str(e).replace('"', '\\"')}"}}')
`]);

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          // Find the JSON output in the response
          const lines = output.split('\n');
          let jsonResult = null;
          
          for (const line of lines) {
            if (line.trim().startsWith('{')) {
              jsonResult = JSON.parse(line.trim());
              break;
            }
          }
          
          if (jsonResult) {
            resolve(jsonResult);
          } else {
            resolve({ success: false, error: 'No valid JSON output found' });
          }
        } catch (parseError) {
          resolve({ success: false, error: `JSON parse error: ${parseError.message}` });
        }
      } else {
        resolve({ success: false, error: `Python process exited with code ${code}: ${errorOutput}` });
      }
    });

    // Set a timeout for the Python process
    setTimeout(() => {
      pythonProcess.kill();
      resolve({ success: false, error: 'RAG query timeout' });
    }, 10000); // 10 second timeout
  });
}

/**
 * Get RAG context for a given query
 * @param {string} text The user's input text
 * @returns {Promise<string>} RAG context to prepend to the message
 */
async function getRAGContext(text) {
  const config = readConfig();
  
  // Check if RAG is enabled
  if (!config.aws?.ragEnabled) {
    console.log('[RAG] RAG is disabled in configuration');
    return '';
  }

  // Initialize RAG system if needed
  if (!ragSystemReady && !ragSystemError) {
    await initializeRAGSystem();
  }

  // If RAG system is not ready, return empty context
  if (!ragSystemReady) {
    console.log('[RAG] RAG system not ready, proceeding without context');
    return '';
  }

  try {
    console.log(`[RAG] Searching for context related to: "${text.substring(0, 50)}..."`);
    
    const ragResult = await runPythonRAGQuery(text);
    
    if (ragResult.success && ragResult.context && ragResult.context.trim()) {
      console.log(`[RAG] ✅ Found relevant context (${ragResult.chunks_found} chunks)`);
      
      // Format the context to be added to the message
      const contextHeader = "\n\n=== RELEVANT INFORMATION FROM KNOWLEDGE BASE ===\n";
      const contextFooter = "\n=== END KNOWLEDGE BASE ===\n\n";
      
      return contextHeader + ragResult.context + contextFooter;
    } else {
      console.log('[RAG] No relevant context found');
      return '';
    }
  } catch (error) {
    console.error(`[RAG] Error retrieving context: ${error.message}`);
    return '';
  }
}

/**
 * Ask Claude a question with RAG enhancement
 * @param {string} text The text to send to Claude
 * @param {Object} opts Options for the request
 * @returns {Promise<string>} A promise that resolves to the reply text
 */
async function askClaudeWithRAG(text, opts = {}) {
  // Add the request to the queue and process it
  return new Promise((resolve, reject) => {
    requestQueue.push(async () => {
      try {
        // Get RAG context first
        const ragContext = await getRAGContext(text);
        
        // Enhance the original text with RAG context if available
        const enhancedText = ragContext ? text + ragContext : text;
        
        // Log what we're doing
        if (ragContext) {
          console.log('[RAG] Enhanced message with knowledge base context');
        } else {
          console.log('[RAG] Proceeding with original message (no additional context)');
        }
        
        const response = await sendClaudeRequest(enhancedText, opts);
        resolve(response);
        return response;
      } catch (error) {
        console.error('RAG-enhanced Claude request failed:', error);
        reject(error);
        throw error;
      }
    });
    
    processQueue();
  });
}

/**
 * Process the request queue
 */
async function processQueue() {
  if (isProcessing || requestQueue.length === 0) {
    return;
  }
  
  isProcessing = true;
  
  try {
    const request = requestQueue.shift();
    if (request) {
      await request();
    }
  } catch (error) {
    console.error('Error processing RAG-enhanced Claude request:', error);
  } finally {
    isProcessing = false;
    
    // Process the next request in the queue
    if (requestQueue.length > 0) {
      processQueue();
    }
  }
}

/**
 * Send a request to the Claude API (same as original implementation)
 * @param {string} text The text to send to Claude
 * @param {Object} opts Options for the request
 * @returns {Promise<string>} A promise that resolves to Claude's response
 */
async function sendClaudeRequest(text, opts = {}) {
  const config = readConfig();
  const httpBase = config.httpBase;
  
  if (!httpBase) {
    throw new Error('HTTP base URL is not configured');
  }
  
  const url = `${httpBase}/claude`;
  const timeoutMs = opts.timeoutMs || 30000; // Default timeout: 30 seconds
  
  console.log(`[Claude] Sending request to ${url}`);
  console.log(`[Claude] Request text: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`);
  
  // Create an AbortController for timeout handling
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    // Prepare the request
    const request = { text };
    
    // Send the request
    const startTime = Date.now();
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
    
    // Clear the timeout
    clearTimeout(timeoutId);
    
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
      
      console.error(`[Claude] ${errorMessage}`);
      throw new Error(errorMessage);
    }
    
    // Parse the response
    const data = await response.json();
    
    // Check if the reply is missing
    if (!data.reply) {
      console.error('[Claude] Invalid response: missing reply field');
      throw new Error('Invalid response: missing reply field');
    }
    
    // Cache the response
    lastResponse = data;
    
    // Log the response time
    const duration = Date.now() - startTime;
    console.log(`[Claude] Response received in ${duration}ms`);
    console.log(`[Claude] Response: ${data.reply.substring(0, 100)}${data.reply.length > 100 ? '...' : ''}`);
    
    return data.reply;
  } catch (error) {
    // Clear the timeout if there was an error
    clearTimeout(timeoutId);
    
    // Handle abort errors
    if (error.name === 'AbortError') {
      console.error('[Claude] Request timed out');
      throw new Error('Request timed out');
    }
    
    // Re-throw other errors
    console.error(`[Claude] Error: ${error.message}`);
    throw error;
  }
}

/**
 * Get the last Claude response
 * @returns The last Claude response, or null if there was no response yet
 */
function getLastClaudeResponse() {
  return lastResponse;
}

/**
 * Check if RAG system is available and ready
 * @returns {boolean} True if RAG system is ready
 */
function isRAGReady() {
  return ragSystemReady;
}

/**
 * Get RAG system status
 * @returns {Object} RAG system status information
 */
function getRAGStatus() {
  return {
    ready: ragSystemReady,
    error: ragSystemError,
    enabled: readConfig().aws?.ragEnabled || false
  };
}

module.exports = { 
  askClaudeWithRAG, 
  getLastClaudeResponse, 
  initializeRAGSystem,
  isRAGReady,
  getRAGStatus,
  // Export original function for backward compatibility
  askClaude: askClaudeWithRAG
};