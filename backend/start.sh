#!/bin/bash
echo "Starting MSME Loan Scorer Backend..."
uvicorn main:app --host 0.0.0.0 --port $PORT
