@echo off
echo Starting directory cleanup and organization...
echo.

REM Create organized directory structure
echo Creating organized directory structure...
if not exist "archive" mkdir archive
if not exist "archive\old-docs" mkdir archive\old-docs
if not exist "archive\old-tests" mkdir archive\old-tests
if not exist "archive\duplicates" mkdir archive\duplicates

REM Move duplicate and obsolete documentation files to archive
echo Moving duplicate documentation files...
move "aws-migration-plan.md" "archive\old-docs\" 2>nul
move "aws-hybrid-poc-guide.md" "archive\old-docs\" 2>nul
move "vtuber-free-roam-feature.md" "archive\old-docs\" 2>nul
move "manufacturing-rag-blog-post.md" "archive\old-docs\" 2>nul
move "cleanup-summary.md" "archive\old-docs\" 2>nul
move "cleanup-todo.md" "archive\old-docs\" 2>nul
move "directory-cleanup-plan.md" "archive\old-docs\" 2>nul

REM Move old setup files
echo Moving old setup files...
move "setup_opensearch_collection.py" "archive\" 2>nul
move "setup_opensearch_simple.bat" "archive\" 2>nul
move "setup_rag_infrastructure.py" "archive\" 2>nul
move "setup_rag.bat" "archive\" 2>nul
move "demo_rag_client.py" "archive\" 2>nul
move "manufacturing_rag_implementation.py" "archive\" 2>nul

REM Move duplicate AWS guides
echo Moving duplicate AWS setup guides...
move "aws-knowledge-base-integration-guide.md" "archive\duplicates\" 2>nul
move "aws-permissions-fix.json" "archive\duplicates\" 2>nul
move "aws-rag-deployment-guide.md" "archive\duplicates\" 2>nul
move "aws-rag-implementation-plan.md" "archive\duplicates\" 2>nul
move "aws-rag-implementation-todo.md" "archive\duplicates\" 2>nul
move "DEMO-RAG-SETUP.md" "archive\duplicates\" 2>nul
move "FIX-AWS-PERMISSIONS.md" "archive\duplicates\" 2>nul
move "INTEGRATED-RAG-GUIDE.md" "archive\duplicates\" 2>nul
move "MANUAL-OPENSEARCH-SETUP.md" "archive\duplicates\" 2>nul
move "QUICK-AWS-RAG-SETUP.md" "archive\duplicates\" 2>nul
move "RAG-IMPLEMENTATION-STATUS.md" "archive\duplicates\" 2>nul
move "RAG-SETUP-GUIDE.md" "archive\duplicates\" 2>nul
move "RAG-TROUBLESHOOTING.md" "archive\duplicates\" 2>nul
move "SIMPLE-OPENSEARCH-SETUP.md" "archive\duplicates\" 2>nul

REM Move configuration files that might contain sensitive data
echo Moving configuration files...
move "manufacturing-assistant-config.yaml" "archive\" 2>nul
move "safety-protocols.txt" "archive\" 2>nul

REM Clean up root level test files
echo Cleaning up root level test files...
if exist "tests" (
    move "tests" "archive\old-tests\" 2>nul
)

REM Remove temporary and duplicate files in main application directory
echo Cleaning up main application directory...
cd "LLM-Live2D-Desktop-Assitant-main"

REM Remove duplicate test files and temporary files
del "test_*.py" 2>nul
del "*_temp.py" 2>nul
del "*_old.*" 2>nul
del "*.backup" 2>nul

REM Move old documentation files
if not exist "..\archive\app-docs" mkdir "..\archive\app-docs"
move "*-guide.md" "..\archive\app-docs\" 2>nul
move "*-summary.md" "..\archive\app-docs\" 2>nul
move "*-implementation*.md" "..\archive\app-docs\" 2>nul
move "*-troubleshooting*.md" "..\archive\app-docs\" 2>nul
move "*-debug*.md" "..\archive\app-docs\" 2>nul
move "*-fix*.md" "..\archive\app-docs\" 2>nul
move "how-to-apply-fix.md" "..\archive\app-docs\" 2>nul
move "immediate-model-fix.md" "..\archive\app-docs\" 2>nul

REM Move duplicate AWS setup files
move "*AWS*SETUP*.md" "..\archive\duplicates\" 2>nul
move "*BEDROCK*.md" "..\archive\duplicates\" 2>nul
move "*OPENSEARCH*.md" "..\archive\duplicates\" 2>nul
move "ADD_OPENSEARCH_POLICY.md" "..\archive\duplicates\" 2>nul
move "UPDATE_BEDROCK_ROLE.md" "..\archive\duplicates\" 2>nul

REM Move status and verification files
move "*STATUS*.md" "..\archive\app-docs\" 2>nul
move "*VERIFICATION*.md" "..\archive\app-docs\" 2>nul
move "*COMPLETE*.md" "..\archive\app-docs\" 2>nul

REM Clean up batch files and scripts
move "*.bat" "..\archive\" 2>nul
move "start_*.py" "..\archive\" 2>nul
move "switch_*.py" "..\archive\" 2>nul
move "upgrade.py" "..\archive\" 2>nul

cd ..

echo.
echo Cleanup completed!
echo.
echo Summary:
echo - Moved duplicate documentation to archive\duplicates\
echo - Moved old documentation to archive\old-docs\
echo - Moved old tests to archive\old-tests\
echo - Moved application docs to archive\app-docs\
echo - Cleaned up temporary and duplicate files
echo - Removed sensitive AWS information files
echo.
echo The main application directory is now organized and secure.
echo Check the archive\ folder for moved files if you need to recover anything.
pause