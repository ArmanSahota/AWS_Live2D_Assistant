/**
 * Node.js Pipeline Test Script
 * Tests TTS, STT, and Claude API endpoints via HTTP
 */

const http = require('http');

const BASE_URL = 'http://localhost:8000';

// Helper function to make HTTP requests
function makeRequest(options, data = null) {
    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => {
                body += chunk;
            });
            res.on('end', () => {
                try {
                    const result = {
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: res.headers['content-type']?.includes('application/json') ? JSON.parse(body) : body
                    };
                    resolve(result);
                } catch (e) {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: body
                    });
                }
            });
        });

        req.on('error', (err) => {
            reject(err);
        });

        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

// Test health endpoint
async function testHealth() {
    console.log('\n=== Testing Health Endpoint ===');
    try {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: '/health',
            method: 'GET'
        };

        const response = await makeRequest(options);
        console.log(`Status: ${response.statusCode}`);
        console.log(`Response:`, response.body);
        
        if (response.statusCode === 200 && response.body.status === 'ok') {
            console.log('✅ Health check PASSED');
            return true;
        } else {
            console.log('❌ Health check FAILED');
            return false;
        }
    } catch (error) {
        console.log('❌ Health check ERROR:', error.message);
        return false;
    }
}

// Test Claude API endpoint
async function testClaude() {
    console.log('\n=== Testing Claude API ===');
    try {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: '/claude',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const data = {
            text: "Hello Claude! This is a test of the pipeline. Please respond briefly."
        };

        const response = await makeRequest(options, data);
        console.log(`Status: ${response.statusCode}`);
        
        if (response.statusCode === 200) {
            console.log(`Claude Response: ${response.body.reply || response.body}`);
            console.log('✅ Claude API PASSED');
            return true;
        } else {
            console.log('❌ Claude API FAILED:', response.body);
            return false;
        }
    } catch (error) {
        console.log('❌ Claude API ERROR:', error.message);
        return false;
    }
}

// Test Mock TTS endpoint
async function testMockTTS() {
    console.log('\n=== Testing Mock TTS API ===');
    try {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: '/api/tts/mock',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const data = {
            text: "This is a test of the text-to-speech system.",
            voice: "en-US-JennyNeural"
        };

        const response = await makeRequest(options, data);
        console.log(`Status: ${response.statusCode}`);
        
        if (response.statusCode === 200) {
            console.log(`TTS Response:`, response.body);
            console.log('✅ Mock TTS API PASSED');
            return true;
        } else {
            console.log('❌ Mock TTS API FAILED:', response.body);
            return false;
        }
    } catch (error) {
        console.log('❌ Mock TTS API ERROR:', error.message);
        return false;
    }
}

// Test Mock STT endpoint
async function testMockSTT() {
    console.log('\n=== Testing Mock STT API ===');
    try {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: '/api/stt/mock',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const data = {
            audio: "mock_base64_audio_data",
            language: "en"
        };

        const response = await makeRequest(options, data);
        console.log(`Status: ${response.statusCode}`);
        
        if (response.statusCode === 200) {
            console.log(`STT Response:`, response.body);
            console.log('✅ Mock STT API PASSED');
            return true;
        } else {
            console.log('❌ Mock STT API FAILED:', response.body);
            return false;
        }
    } catch (error) {
        console.log('❌ Mock STT API ERROR:', error.message);
        return false;
    }
}

// Test static file serving
async function testStaticFiles() {
    console.log('\n=== Testing Static File Serving ===');
    try {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: '/static/desktop.html',
            method: 'GET'
        };

        const response = await makeRequest(options);
        console.log(`Status: ${response.statusCode}`);
        
        if (response.statusCode === 200) {
            console.log('✅ Static files PASSED - desktop.html is accessible');
            return true;
        } else {
            console.log('❌ Static files FAILED - desktop.html not accessible');
            return false;
        }
    } catch (error) {
        console.log('❌ Static files ERROR:', error.message);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Starting Pipeline Tests...');
    console.log('=' * 50);

    const results = {
        health: await testHealth(),
        claude: await testClaude(),
        mockTTS: await testMockTTS(),
        mockSTT: await testMockSTT(),
        staticFiles: await testStaticFiles()
    };

    console.log('\n' + '='.repeat(50));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(50));

    let passed = 0;
    let total = 0;

    Object.entries(results).forEach(([test, result]) => {
        const status = result ? '✅ PASS' : '❌ FAIL';
        console.log(`${test.padEnd(15)}: ${status}`);
        if (result) passed++;
        total++;
    });

    console.log('='.repeat(50));
    console.log(`Results: ${passed}/${total} tests passed`);
    
    if (passed === total) {
        console.log('🎉 All tests PASSED! Pipeline is working correctly.');
    } else {
        console.log('⚠️  Some tests FAILED. Check the output above for details.');
    }

    return results;
}

// Run the tests
if (require.main === module) {
    runAllTests().catch(console.error);
}

module.exports = { runAllTests, testHealth, testClaude, testMockTTS, testMockSTT, testStaticFiles };