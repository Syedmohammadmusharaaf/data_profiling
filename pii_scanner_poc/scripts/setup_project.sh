#!/bin/bash
# PII/PHI Scanner POC - Setup Script (Unix/Linux/macOS)

echo "========================================"
echo "PII/PHI Scanner POC - Project Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Python found. Creating virtual environment..."
echo ""

# Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully."
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated."
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
echo ""
pip install langchain-openai==0.3.27
pip install langchain-core==0.3.68
pip install openai==1.93.1
pip install tiktoken==0.9.0
pip install configparser
pip install pyodbc
pip install mysql-connector-python
pip install oracledb
pip install openpyxl
pip install pandas
pip install python-dotenv

# Confirm installation
echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "To run the PII/PHI Scanner:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run scanner: python pii_scanner.py"
echo ""
echo "To update your API key:"
echo "1. Edit the .env file"
echo "2. Update AZURE_OPENAI_API_KEY with your actual key"
echo ""