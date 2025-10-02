# Puppeteer MCP Self-Testing Instructions

## Overview
This document provides instructions for using the Puppeteer MCP (Model Context Protocol) to self-test frontend changes and functionality without manual supervision. This allows AI coding agents to iterate on tasks autonomously while minimizing API credit usage.

## Prerequisites
- Puppeteer MCP must be configured and running
- Backend server must be running on http://localhost:8000
- Frontend server must be running on http://localhost:5173

## Authentication Details
- **Admin Username**: admin (or as configured during setup)
- **Admin Password**: firesnake
- **Secret Question Answer**: "i will defy the heavens" (for first-time admin setup)

## Test Workflow

### 1. Initial Setup and Navigation
```javascript
// Start by navigating to the application
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173" })

// Take initial screenshot for reference
await mcp__puppeteer__puppeteer_screenshot({ name: "initial_state" })
```

### 2. Admin Login Testing
```javascript
// Navigate to admin login
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173/admin" })

// Fill login credentials
await mcp__puppeteer__puppeteer_fill({ selector: "#username", value: "admin" })
await mcp__puppeteer__puppeteer_fill({ selector: "#password", value: "firesnake" })

// Click login button
await mcp__puppeteer__puppeteer_click({ selector: "button[type='submit']" })

// Wait and verify successful login
await mcp__puppeteer__puppeteer_evaluate({ script: "new Promise(r => setTimeout(r, 2000))" })
await mcp__puppeteer__puppeteer_screenshot({ name: "admin_dashboard" })
```

### 3. Chat Interface Testing
```javascript
// Navigate to chat interface
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173/chat" })

// Wait for chat to load
await mcp__puppeteer__puppeteer_evaluate({ script: "new Promise(r => setTimeout(r, 1000))" })

// Test message sending
await mcp__puppeteer__puppeteer_fill({
  selector: ".tiptap.ProseMirror",
  value: "Test message from Puppeteer"
})

// Submit message (look for send button or use Enter key simulation)
await mcp__puppeteer__puppeteer_click({ selector: "button[aria-label='Send message']" })

// Wait for response
await mcp__puppeteer__puppeteer_evaluate({ script: "new Promise(r => setTimeout(r, 3000))" })
await mcp__puppeteer__puppeteer_screenshot({ name: "chat_response" })
```

### 4. Key Areas to Test

#### Chat Functionality
- Message sending and receiving
- WebSocket connection status
- Streaming response display
- Math rendering (test with LaTeX expressions)
- Code highlighting (test with code blocks)
- Conversation history navigation
- New conversation creation

#### Admin Dashboard
- Queue monitoring display
- System statistics
- User management
- Token generation
- API key management

#### Authentication Flow
- User login/logout
- Registration with token
- Session persistence
- Protected route access

## Efficient Testing Strategies

### 1. Session Persistence (Token Optimization)
**CRITICAL**: The Puppeteer MCP maintains browser sessions between calls. Avoid repeated logins to save tokens:

```javascript
// ✅ GOOD: Login once, then reuse session
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173/admin" })
// ... perform login ...

// Later tests - session is preserved
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173/chat" })
// No need to login again! Session persists.

// ❌ BAD: Logging in for every test wastes tokens
```

**Best Practices**:
- Login once at start of testing session
- Test multiple features in same session
- Only login again if explicitly testing auth flows

### 2. Minimal Screenshots
Only capture screenshots at critical points:
- After navigation to verify page load
- After form submission to verify result
- When errors occur for debugging

### 3. Use Evaluation for Checks
Instead of screenshots, use JavaScript evaluation for verification:
```javascript
// Check if element exists
const exists = await mcp__puppeteer__puppeteer_evaluate({
  script: "document.querySelector('.error-message') !== null"
})

// Get element text
const text = await mcp__puppeteer__puppeteer_evaluate({
  script: "document.querySelector('.status').textContent"
})

// Check WebSocket connection
const wsConnected = await mcp__puppeteer__puppeteer_evaluate({
  script: "window.wsConnection?.readyState === 1"
})
```

### 3. Batch Testing
Test multiple features in a single session to minimize setup overhead:
1. Navigate once
2. Test multiple UI elements
3. Capture final state

### 4. Error Detection Patterns
```javascript
// Check for React error boundaries
const hasError = await mcp__puppeteer__puppeteer_evaluate({
  script: `
    const errorBoundary = document.querySelector('[data-error-boundary]');
    const consoleErrors = window.__capturedErrors || [];
    return errorBoundary !== null || consoleErrors.length > 0;
  `
})

// Check for network errors
const networkErrors = await mcp__puppeteer__puppeteer_evaluate({
  script: `
    performance.getEntriesByType('resource')
      .filter(e => e.responseStatus >= 400).length > 0
  `
})
```

## Common Test Scenarios

### 1. Testing After Code Changes
```javascript
// 1. Navigate to affected page
// 2. Perform action that uses changed code
// 3. Verify expected behavior
// 4. Check for console errors
```

### 2. Testing New Features
```javascript
// 1. Navigate to feature location
// 2. Interact with new UI elements
// 3. Verify data flow
// 4. Test edge cases
```

### 3. Regression Testing
```javascript
// 1. Test primary user flows
// 2. Verify critical functionality still works
// 3. Check for visual regressions (compare screenshots)
```

## Tips for AI Agents

1. **Start Simple**: Begin with navigation and basic interactions before complex flows
2. **Use Selectors Wisely**: Prefer stable selectors (IDs, data-attributes) over classes
3. **Handle Async**: Always wait for dynamic content to load
4. **Incremental Testing**: Test small changes frequently rather than large batches
5. **Error Recovery**: If a test fails, try alternative selectors or approaches
6. **Console Monitoring**: Inject console error capture early in the session

## Example Complete Test Flow
```javascript
// Setup error capture
await mcp__puppeteer__puppeteer_evaluate({
  script: "window.__capturedErrors = []; window.addEventListener('error', e => window.__capturedErrors.push(e.message))"
})

// Navigate and login
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173" })
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:5173/admin" })
await mcp__puppeteer__puppeteer_fill({ selector: "#username", value: "admin" })
await mcp__puppeteer__puppeteer_fill({ selector: "#password", value: "firesnake" })
await mcp__puppeteer__puppeteer_click({ selector: "button[type='submit']" })

// Wait for dashboard
await mcp__puppeteer__puppeteer_evaluate({ script: "new Promise(r => setTimeout(r, 2000))" })

// Check for errors
const errors = await mcp__puppeteer__puppeteer_evaluate({
  script: "window.__capturedErrors"
})

if (errors.length === 0) {
  // Continue with feature testing
} else {
  // Investigate errors
  await mcp__puppeteer__puppeteer_screenshot({ name: "error_state" })
}
```

## Headless vs Headed Mode
For debugging, you can run Puppeteer in headed mode to see what's happening:
```javascript
await mcp__puppeteer__puppeteer_navigate({
  url: "http://localhost:5173",
  launchOptions: { headless: false }
})
```
Note: Use headless mode (default) for regular testing to save resources.