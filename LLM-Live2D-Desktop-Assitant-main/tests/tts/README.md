# TTS Tests

This directory contains tests for the Text-to-Speech (TTS) functionality of the LLM-Live2D-Desktop-Assistant project.

## Overview

The TTS tests are designed to verify the functionality of the TTS engines and the TTS factory. The tests use a combination of mock objects and real TTS engines to ensure that the TTS functionality works as expected.

## Test Files

- `mock_tts.py`: A mock TTS engine that simulates the behavior of a real TTS engine without actually generating audio.
- `mock_tts_factory.py`: A mock TTS factory that returns mock TTS engines for testing.
- `test_tts.py`: The main test file that contains the test cases for the TTS functionality.
- `run_tts_tests.js`: A JavaScript wrapper for running the Python TTS tests from the main test runner.

## Running the Tests

You can run the TTS tests using the main test runner:

```bash
node tests/index.js tts
```

Or you can run the Python tests directly:

```bash
python tests/tts/test_tts.py
```

## Test Cases

The TTS tests include the following test cases:

1. **Mock TTS Engine Test**: Tests the functionality of the mock TTS engine, including:
   - Setting the voice
   - Generating audio files
   - Verifying the generated text

2. **Mock TTS Factory Test**: Tests the functionality of the mock TTS factory, including:
   - Creating a mock TTS engine
   - Verifying that the engine has the correct voice
   - Generating audio files

3. **Real TTS Factory Test**: Tests the functionality of the real TTS factory with a simple TTS engine (pyttsx3TTS). This test is skipped if the required dependencies are not installed.

## Adding New Tests

To add a new TTS test:

1. Add your test case to the `test_tts.py` file.
2. If your test requires additional mock objects, add them to the appropriate mock files.
3. Update this README.md file to include information about your new test.

## Dependencies

The TTS tests require the following dependencies:

- Python 3.6 or higher
- unittest (part of the Python standard library)
- pyttsx3 (optional, for testing real TTS engines)
