@echo off
echo ========================================
echo RAG Vision Integration Setup and Test
echo ========================================
echo.

echo Step 1: Setting up RAG documents...
call add_rag_documents.bat
echo.

echo Step 2: Testing RAG vision integration...
python test_rag_vision_integration.py
echo.

echo Step 3: Ready to test!
echo.
echo To test the RAG-enhanced vision analysis:
echo 1. Run: python server.py
echo 2. Open desktop.html in your browser
echo 3. Click the "📁 Upload Image" button
echo 4. Upload your heater error image
echo 5. See the enhanced manufacturing analysis!
echo.

pause