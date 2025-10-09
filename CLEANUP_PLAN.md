# Directory Cleanup and Organization Plan

## 🚨 SECURITY ISSUES IDENTIFIED

### Sensitive Information Found:
- **AWS Account ID**: `615299772411` (found in 41+ files)
- **AWS User ID**: `AIDAY6QVZN75RIFWX3JXE`
- **AWS ARNs**: Multiple files contain specific resource ARNs
- **References to AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY** in documentation

### Files Containing Sensitive Data:
- `LLM-Live2D-Desktop-Assitant-main/YOUR_AWS_INFO.md` ⚠️ **CRITICAL**
- Multiple setup guides with hardcoded account IDs
- Configuration files with AWS resource ARNs

## 📁 DIRECTORY ORGANIZATION PLAN

### 1. Root Level Cleanup
**Keep:**
- `.gitignore` (enhanced)
- `README.md` (cleaned)
- `package.json` / `package-lock.json`
- Main application directory

**Move to Archive:**
- Duplicate documentation files
- Old test files at root level
- Temporary setup files

**Delete:**
- Files with sensitive AWS information
- Duplicate/obsolete files
- Test output files

### 2. Documentation Restructure
**Current Issues:**
- Documentation scattered across multiple locations
- Duplicate guides with different information
- Sensitive information in docs

**Proposed Structure:**
```
docs/
├── setup/           # Installation and configuration
├── guides/          # User guides (cleaned)
├── api/            # API documentation
├── troubleshooting/ # Issue resolution
└── architecture/    # System design docs
```

### 3. Main Application Directory
**LLM-Live2D-Desktop-Assitant-main/** needs:
- Remove sensitive AWS info files
- Consolidate duplicate test files
- Clean up temporary/debug files
- Organize by functionality

## 🗑️ FILES TO DELETE

### Root Level:
- `safety-protocols.txt` (move to docs if needed)
- Duplicate AWS setup files
- Old migration plans at root

### Sensitive Files (MUST DELETE):
- `LLM-Live2D-Desktop-Assitant-main/YOUR_AWS_INFO.md`
- Any file containing actual AWS credentials
- Files with hardcoded account IDs

### Duplicate/Obsolete Files:
- Multiple versions of same guides
- Old test files
- Temporary setup scripts

## 🔒 GITIGNORE ENHANCEMENTS NEEDED

### Add to .gitignore:
- AWS credential files
- Environment files with secrets
- Local configuration files
- Build artifacts
- Test outputs
- Temporary files

## 📋 EXECUTION STEPS

1. **IMMEDIATE**: Update .gitignore with security rules
2. **CRITICAL**: Remove/sanitize files with sensitive AWS data
3. **ORGANIZE**: Restructure documentation
4. **CLEAN**: Remove duplicate and obsolete files
5. **VERIFY**: Ensure no sensitive data remains

## ⚠️ SECURITY RECOMMENDATIONS

1. **Never commit AWS credentials** to version control
2. **Use environment variables** for sensitive configuration
3. **Template files** should use placeholders like `YOUR_ACCOUNT_ID`
4. **Regular audits** for sensitive information
5. **Use AWS IAM roles** instead of hardcoded credentials where possible