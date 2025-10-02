# CLAUDE.md

## Project: Inkmortal Local LLM Server

A self-hosted AI assistant platform running on Mac M4 hardware, providing free LLM capabilities to family and friends without ongoing API costs.

## Quick Access

### Admin Login
- URL: http://localhost:5173/admin
- Password: firesnake
- First-time setup secret: "i will defy the heavens"

### Development Servers
```bash
# Backend: cd backend && python -m uvicorn app.main:app --reload --port 8000
# Frontend: cd frontend && npm run dev
```

## Critical Development Rules

### Refactoring Guidelines
- **NO "v2", "new", "old" file naming** - Replace existing files instead of creating duplicates
- **Files can be up to 800 lines** (previously 400)
- **Comments are allowed** in code files

### Code Reuse Principles
- **ALWAYS check for existing functionality** before creating new functions/variables
- **NEVER assume a function exists** without verifying it first
- **AVOID recreating** existing functionality - search and reuse
- **NO unnecessary backwards compatibility** - This is a personal project, not enterprise software
- **NO legacy system handling** unless explicitly requested

### Before Creating ANY New Function/Variable
1. Search the codebase for similar functionality
2. Check imports and existing utilities
3. Look at neighboring files for patterns
4. Only create new if truly needed

## Testing & Debugging Resources

@PUPPETEER-TESTING.md
@AI-DEBUGGING-BEST-PRACTICES.md

## Memory Bank

@memory-bank-instructions.md

### Key Memory Files
- `memory-bank/projectbrief.md` - Core requirements and goals
- `memory-bank/activeContext.md` - Current work and recent changes
- `memory-bank/systemPatterns.md` - Architecture patterns
- `memory-bank/techContext.md` - Technology details
- `memory-bank/progress.md` - Development status

## Multi-Model Assistance (Zen MCP)

Use different models for their strengths:
- **Gemini** (`gemini-2.5-pro`): Architecture, planning, system design
- **GPT** (`gpt-5`): Code implementation, algorithms, specific features

Example: `mcp__zen__chat({ model: "gemini-2.5-pro", prompt: "...", files: ["..."] })`

## Important Testing Commands

```bash
# Run after code changes
npm run lint      # Frontend linting
npm run typecheck # TypeScript checking
npx tsc          # TypeScript compilation
```

## Code Conventions

- Follow existing patterns in similar files
- Always check package.json before adding dependencies
- Use proper TypeScript types
- Single source of truth for state management
- Prefer editing existing files over creating new ones
