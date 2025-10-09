# Directory Cleanup Plan

## Overview
This plan organizes the AWS VTuber LLM project by:
1. Moving all MD files to a dedicated documentation folder
2. Consolidating all test files into the existing tests directory
3. Identifying and removing unnecessary/outdated files

## Current Issues Identified

### 1. Scattered MD Files (60+ files)
**Location**: `LLM-Live2D-Desktop-Assitant-main/` root directory
**Problem**: Documentation files are mixed with source code

**MD Files to Organize**:
- Architecture & Implementation docs: `ARCHITECTURE_DIAGRAM.md`, `live2d-*.md`
- Fix & Diagnostic docs: `*_FIX*.md`, `*_DIAGNOSTIC*.md`
- Migration & Setup docs: `AWS_*.md`, `MIGRATION_*.md`, `PHASE*.md`
- Troubleshooting docs: `TROUBLESHOOTING_GUIDE.md`, `DEBUG_*.md`
- Project docs: `README.md`, `README.CN.md`

### 2. Scattered Test Files (30+ files)
**Location**: `LLM-Live2D-Desktop-Assitant-main/` root directory
**Problem**: Test files mixed with main application code

**Test Files to Move**:
```
test_*.py (25+ files)
test_*.js (8+ files)  
test-*.html (1 file)
test-*.bat (2 files)
diagnostic_*.py (5+ files)
*_diagnostic.py (10+ files)
```

### 3. Unnecessary/Outdated Files
**Categories**:
- Duplicate diagnostic files
- Temporary fix files
- Old migration reports
- Debug scripts that are no longer needed

## Proposed Directory Structure

```
LLM-Live2D-Desktop-Assitant-main/
├── docs/                          # NEW: All documentation
│   ├── architecture/              # Architecture & design docs
│   ├── fixes/                     # Fix documentation & reports
│   ├── migration/                 # Migration & setup guides
│   ├── troubleshooting/           # Debug & troubleshooting
│   ├── live2d/                    # Live2D specific docs
│   └── README.md                  # Main project README
├── tests/                         # EXPANDED: All test files
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── diagnostics/               # Diagnostic scripts
│   ├── vision/                    # Vision system tests
│   ├── audio/                     # Audio pipeline tests
│   ├── claude/                    # Claude API tests
│   └── websocket/                 # WebSocket tests
├── [existing source directories]
└── [clean root with only essential files]
```

## Implementation Steps

### Phase 1: Create Documentation Structure
1. Create `docs/` directory with subdirectories
2. Move and categorize all MD files
3. Update any internal links

### Phase 2: Organize Test Files
1. Expand `tests/` directory structure
2. Move all test files to appropriate subdirectories
3. Update test runner configurations

### Phase 3: Remove Unnecessary Files
1. Identify truly obsolete files
2. Archive important historical files
3. Delete redundant/temporary files

### Phase 4: Clean Root Directory
1. Keep only essential files in root
2. Update documentation references
3. Verify all functionality still works

## Files to Keep in Root
- `main.py`, `main.js` (entry points)
- `package.json`, `requirements.txt` (dependencies)
- `README.md` (moved from docs)
- `.env*`, `.git*` (configuration)
- `dockerfile`, `tsconfig.json` (build config)
- Essential startup scripts

## Files Likely Safe to Delete
- Multiple `*_COMPLETE.md` files (migration completion reports)
- Duplicate diagnostic files
- Old fix validation files
- Temporary debug scripts
- Phase completion summaries (after archiving key info)

## Risk Mitigation
1. **Backup**: Create full backup before starting
2. **Incremental**: Move files in small batches
3. **Testing**: Verify functionality after each phase
4. **Documentation**: Update all references and paths
5. **Rollback Plan**: Keep moved files accessible for 30 days

## Success Criteria
- Root directory contains <20 files
- All MD files organized in logical structure
- All tests consolidated and categorized
- No broken functionality
- Clear navigation for developers
- Improved project maintainability