# Tests Directory

This directory contains organized tests for the LLM-Live2D-Desktop-Assistant project. The tests are categorized by functionality to make it easier to maintain and run specific test suites.

## Directory Structure

```
tests/
├── index.js         # Main test runner
├── aws/            # AWS-related tests (Claude API, etc.)
├── http/           # HTTP API tests
├── ws/             # WebSocket tests
├── config/         # Configuration loading tests
├── electron/       # Electron app tests
└── tts/            # Text-to-Speech tests
```

## Running Tests

You can run tests using the main test runner:

```bash
# Show available test categories
node tests/index.js

# Run all tests in a category
node tests/index.js aws

# Run a specific test
node tests/index.js http test_http
```

## Test Categories

### AWS Tests
Tests related to AWS services, particularly Claude API integration.

### HTTP Tests
Tests for HTTP API functionality.

### WebSocket Tests
Tests for WebSocket communication.

### Config Tests
Tests for configuration loading and validation.

### Electron Tests
Tests for Electron app functionality.

### TTS Tests
Tests for Text-to-Speech functionality. These tests use Python and include:
- Mock TTS engine tests
- Mock TTS factory tests
- Real TTS engine tests (skipped if dependencies are not installed)

## Adding New Tests

To add a new test:

1. Place your test file in the appropriate category directory
2. Make sure your test file exports a main function or is executable as a standalone script
3. Follow the naming convention: `test_[feature].js`

## Best Practices

- Each test should be focused on testing a specific functionality
- Tests should be independent and not rely on the state from other tests
- Use descriptive names for test files and functions
- Add comments to explain complex test scenarios
