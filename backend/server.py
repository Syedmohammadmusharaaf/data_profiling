#!/usr/bin/env python3
"""
Server entry point for PII Scanner Backend
Imports the FastAPI app from main.py
"""

import sys
import os

# Add the parent directory to Python path to find pii_scanner_poc
sys.path.insert(0, '/app')

from simple_main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)