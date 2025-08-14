#!/bin/bash
echo "=== Debug Startup Script ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo ""
echo "=== Python path ==="
which python
python --version

echo ""
echo "=== Trying to run uvicorn ==="
echo "Command: uvicorn main:app --host 0.0.0.0 --port $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT
