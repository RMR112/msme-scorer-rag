@echo off
REM MSME Loan Scorer with LightRAG - Startup Script for Windows

echo 🚀 Starting MSME Loan Scorer with LightRAG...

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found!
    echo Please create a .env file with your OPENAI_API_KEY
    echo Example:
    echo OPENAI_API_KEY=your_openai_api_key_here
    echo FRONTEND_ORIGIN=http://localhost:3000
    pause
    exit /b 1
)

REM Check if PDFs exist in backend folder
cd backend
set PDF_COUNT=0
for %%f in (*.pdf) do set /a PDF_COUNT+=1

if %PDF_COUNT%==0 (
    echo ❌ Error: No PDF files found in backend folder!
    echo Please add your PDF documents to the backend/ folder
    pause
    exit /b 1
)

echo ✅ Found %PDF_COUNT% PDF file(s) in backend folder

REM Step 1: Ingest PDFs
echo.
echo 📚 Step 1: Ingesting PDF documents into LightRAG...
python ingest.py

if errorlevel 1 (
    echo ❌ PDF ingestion failed!
    pause
    exit /b 1
)

echo ✅ PDF ingestion completed successfully!

REM Step 2: Start FastAPI server
echo.
echo 🌐 Step 2: Starting FastAPI server...
echo 📖 API documentation will be available at: http://localhost:8000/docs
echo 🔍 Health check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
