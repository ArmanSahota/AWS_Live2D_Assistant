# AI Debugging Best Practices

## Overview
This document outlines best practices for AI agents when debugging code to avoid common pitfalls, infinite loops, and unproductive debugging cycles. These guidelines help AI coding assistants work more effectively and autonomously.

## Core Principles

### 1. Avoid Debugging Theater
**Problem**: Making changes that appear to fix issues but don't address root causes.
**Solution**: Always verify assumptions before implementing fixes.

### 2. Prevent Loop Patterns
**Problem**: Repeating the same debugging approach that already failed.
**Solution**: Track attempted solutions and explicitly try different approaches.

## Common AI Debugging Pitfalls and Solutions

### 1. The Assumption Loop
**Pitfall**: Assuming the cause of an error without verification.
```
❌ BAD: "The error is probably in the API call, let me fix it"
✅ GOOD: "Let me first check the actual error message and stack trace"
```

**Best Practice**:
1. Read the actual error message completely
2. Check the stack trace for the exact location
3. Verify the error is reproducible
4. Test your hypothesis before implementing a fix

### 2. The Shotgun Debugging Anti-Pattern
**Pitfall**: Making multiple unrelated changes hoping something works.
```
❌ BAD: Changing imports, adding console.logs, modifying unrelated code simultaneously
✅ GOOD: Change one thing, test, evaluate, then proceed
```

**Best Practice**:
1. Make ONE change at a time
2. Test after each change
3. Revert changes that don't help
4. Document what you tried and the result

### 3. The Context Blindness Problem
**Pitfall**: Not checking surrounding code or project structure.
```
❌ BAD: Adding a new dependency without checking if it already exists
✅ GOOD: Check package.json, existing imports, and similar files first
```

**Best Practice**:
1. Always check existing code patterns first
2. Look for similar functionality already implemented
3. Read related files before making changes
4. Understand the project's conventions

### 4. The Infinite Retry Loop
**Pitfall**: Trying the same fix repeatedly with minor variations.

**Best Practice - The Three Strike Rule**:
```javascript
// Track attempts
let attempts = {
  "fix_import": 1,
  "modify_config": 1,
  "restart_server": 1
};

// After 3 attempts of similar fixes, STOP and reassess
if (attempts[currentApproach] >= 3) {
  // Step back and try a completely different approach
  // Consider: Different file, different method, ask for help
}
```

### 5. The Missing Feedback Loop
**Pitfall**: Not verifying if changes actually fixed the issue.

**Best Practice - Verification Checklist**:
```markdown
- [ ] Error message is gone
- [ ] Feature works as expected
- [ ] No new errors introduced
- [ ] Tests pass (if applicable)
- [ ] Can reproduce the fix
```

## Systematic Debugging Workflow

### Phase 1: Understand
```
1. Read the COMPLETE error message
2. Identify the error type and location
3. Check if this is a known issue (search codebase)
4. Understand what the code SHOULD do
```

### Phase 2: Hypothesize
```
1. Form a specific hypothesis about the cause
2. Identify how to test this hypothesis
3. Predict what you expect to see
4. Document your hypothesis
```

### Phase 3: Test
```
1. Make the MINIMAL change to test hypothesis
2. Run the code
3. Observe the result
4. Compare with prediction
```

### Phase 4: Iterate or Escalate
```
IF hypothesis confirmed:
  - Implement proper fix
  - Test thoroughly
  - Document the solution
ELSE IF tried 3 different approaches:
  - Step back and reassess
  - Try a fundamentally different angle
  - Consider if the problem is elsewhere
```

## Using Multiple AI Models Effectively

### When to Use Gemini (Architecture/Planning)
- Designing system architecture
- Planning major refactors
- Understanding complex relationships
- Creating high-level strategies

### When to Use GPT (Implementation)
- Writing specific code implementations
- Solving algorithmic problems
- Handling detailed syntax issues
- Creating utility functions

### When to Use Claude (Analysis/Debugging)
- Analyzing existing code
- Finding subtle bugs
- Understanding context
- Comprehensive code reviews

### Example Multi-Model Workflow
```markdown
1. Claude: Analyze the bug and understand context
2. Gemini: Design the solution architecture
3. GPT: Implement the specific fix
4. Claude: Verify and test the solution
```

## Anti-Patterns to Avoid

### 1. The "Works on My Machine" Fallacy
Always consider environment differences:
- Check versions (Node, Python, dependencies)
- Verify paths are correct
- Check environment variables
- Consider OS differences

### 2. The Cargo Cult Fix
Don't copy solutions without understanding:
- Understand WHY a solution works
- Adapt to your specific context
- Test in your environment
- Document the reasoning

### 3. The Hail Mary Refactor
Avoid rewriting everything when stuck:
- Isolate the problem first
- Fix the specific issue
- Refactor separately if needed
- Keep changes minimal

## Self-Diagnostic Checklist

Before each debugging session, ask:
```markdown
- [ ] Have I read the ENTIRE error message?
- [ ] Do I understand what the code should do?
- [ ] Have I checked for similar issues in the codebase?
- [ ] Am I making targeted changes or random attempts?
- [ ] Have I tested my assumptions?
- [ ] Am I stuck in a loop (tried same thing 3+ times)?
- [ ] Should I try a different approach?
```

## Loop Prevention Strategies

### 1. The State Tracker
Keep track of what you've tried:
```javascript
const debugLog = {
  timestamp: Date.now(),
  attempts: [],
  currentHypothesis: "",

  addAttempt(action, result) {
    this.attempts.push({ action, result, time: Date.now() });
    if (this.attempts.filter(a => a.action === action).length >= 3) {
      console.warn(`Tried ${action} 3 times - need new approach`);
    }
  }
};
```

### 2. The Circuit Breaker
Stop infinite debugging loops:
```python
class DebuggingCircuitBreaker:
    def __init__(self, max_similar_attempts=3):
        self.attempts = {}
        self.max_attempts = max_similar_attempts

    def should_continue(self, approach):
        self.attempts[approach] = self.attempts.get(approach, 0) + 1
        if self.attempts[approach] >= self.max_attempts:
            return False, f"Tried {approach} {self.max_attempts} times. Try different approach."
        return True, "Continue"
```

### 3. The Hypothesis Journal
Document your debugging process:
```markdown
## Debug Session: [Issue Description]

### Hypothesis 1: [What you think is wrong]
- Test: [How you'll test it]
- Result: [What happened]
- Conclusion: [Was hypothesis correct?]

### Hypothesis 2: [Different angle]
- Test: [Different test approach]
- Result: [What happened]
- Conclusion: [Learning from this test]

### Solution Found:
- Root Cause: [Actual problem]
- Fix Applied: [What fixed it]
- Prevention: [How to avoid in future]
```

## Quick Reference: When Stuck

1. **Been trying same approach 3+ times?** → Stop, try completely different angle
2. **Making random changes?** → Stop, form specific hypothesis first
3. **Don't understand error?** → Read it completely, search for similar issues
4. **Fix not working?** → Verify assumptions, check if testing correctly
5. **Everything seems broken?** → Revert changes, start with minimal reproducible case
6. **Can't find the bug?** → Use different model (Gemini/GPT) for fresh perspective

## Using Zen MCP for Multi-Model Debugging

When stuck, leverage different models:
```javascript
// Use Gemini for understanding the architecture
await mcp__zen__chat({
  model: "gemini-2.5-pro",
  prompt: "Analyze this system architecture and identify potential failure points",
  files: ["src/problematic-file.js"]
});

// Use GPT for specific implementation
await mcp__zen__chat({
  model: "gpt-5",
  prompt: "Implement a fix for this specific error handling case",
  files: ["src/error-handler.js"]
});

// Use Claude for verification
// (You're Claude, so you handle the final verification)
```

## Remember: Debugging is Detective Work

Good debugging is methodical investigation, not random experimentation. Each test should give you information that helps narrow down the problem. If you're not learning something new from each attempt, you're probably stuck in a loop.

**The Golden Rule**: If you've tried the same type of fix three times without success, it's time to question your assumptions and try a fundamentally different approach.