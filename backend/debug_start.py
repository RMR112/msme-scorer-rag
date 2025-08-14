#!/usr/bin/env python3
import os
import sys

print("=== Debug Startup Script ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Files in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")

print("\n=== Trying to import main ===")
try:
    import main
    print("✅ Successfully imported main")
    print(f"Main app object: {main.app}")
except Exception as e:
    print(f"❌ Failed to import main: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()

print("\n=== Starting uvicorn ===")
