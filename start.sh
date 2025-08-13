#!/bin/bash

# MSME Loan Scorer with LightRAG - Startup Script

echo "🚀 Starting MSME Loan Scorer with LightRAG..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "Example:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "FRONTEND_ORIGIN=http://localhost:3000"
    exit 1
fi

# Check if PDFs exist in backend folder
cd backend
PDF_COUNT=$(ls *.pdf 2>/dev/null | wc -l)
if [ $PDF_COUNT -eq 0 ]; then
    echo "❌ Error: No PDF files found in backend folder!"
    echo "Please add your PDF documents to the backend/ folder"
    exit 1
fi

echo "✅ Found $PDF_COUNT PDF file(s) in backend folder"

# Step 1: Ingest PDFs
echo ""
echo "📚 Step 1: Ingesting PDF documents into LightRAG..."
python ingest.py

if [ $? -ne 0 ]; then
    echo "❌ PDF ingestion failed!"
    exit 1
fi

echo "✅ PDF ingestion completed successfully!"

# Step 2: Start FastAPI server
echo ""
echo "🌐 Step 2: Starting FastAPI server..."
echo "📖 API documentation will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
