@echo off
REM =============================================================================
REM PII/PHI Scanner POC - Windows Setup Script (setup_project.bat)
REM =============================================================================
REM
REM This Windows batch script automates the complete setup process for the
REM PII/PHI Scanner on Windows systems. It handles environment creation,
REM dependency installation, and provides guidance for getting started.
REM
REM FEATURES:
REM - Validates Python installation and version
REM - Creates isolated virtual environment
REM - Installs all required Python dependencies
REM - Provides clear setup status and next steps
REM - Includes error handling and troubleshooting guidance
REM
REM REQUIREMENTS:
REM - Windows 10/11 or Windows Server 2016+
REM - Python 3.8 or higher installed and in PATH
REM - Internet connection for package downloads
REM - Administrator privileges may be required for some operations
REM
REM USAGE:
REM 1. Save this file as setup_project.bat
REM 2. Right-click and "Run as Administrator" (recommended)
REM 3. Follow the on-screen instructions
REM 4. Update .env file with your API credentials after setup completes
REM
REM Author: AI Assistant
REM Version: 1.0 POC
REM =============================================================================

REM Display setup banner
echo ========================================
echo PII/PHI Scanner POC - Project Setup
echo ========================================
echo.
echo This script will set up the PII/PHI Scanner environment on Windows.
echo.
echo Setup process:
echo 1. Validate Python installation
echo 2. Create Python virtual environment  
echo 3. Install required dependencies
echo 4. Verify installation
echo.

REM =============================================================================
REM STEP 1: VALIDATE PYTHON INSTALLATION
REM =============================================================================
echo [STEP 1/4] Validating Python installation...

REM Check if Python is installed and accessible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo RESOLUTION:
    echo 1. Download Python 3.8+ from https://www.python.org/downloads/
    echo 2. During installation, check "Add Python to PATH"
    echo 3. Restart this script after Python installation
    echo.
    echo VERIFICATION:
    echo Open Command Prompt and run: python --version
    echo You should see "Python 3.x.x" displayed
    echo.
    pause
    exit /b 1
)

REM Display Python version for verification
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Found %PYTHON_VERSION%

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: pip is not available with your Python installation
    echo.
    echo RESOLUTION:
    echo 1. Reinstall Python from https://www.python.org/downloads/
    echo 2. Ensure "pip" is selected during installation
    echo 3. Or manually install pip: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

echo ✓ pip is available
echo.

REM =============================================================================
REM STEP 2: CREATE VIRTUAL ENVIRONMENT
REM =============================================================================
echo [STEP 2/4] Creating Python virtual environment...

REM Create virtual environment in 'venv' directory
python -m venv venv
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to create virtual environment
    echo.
    echo POSSIBLE CAUSES:
    echo - Insufficient disk space
    echo - Permission issues in current directory
    echo - Corrupted Python installation
    echo.
    echo RESOLUTION:
    echo 1. Run this script as Administrator
    echo 2. Ensure you have write permissions in this directory
    echo 3. Free up disk space if needed
    echo 4. Try running: python -m venv --clear venv
    echo.
    pause
    exit /b 1
)

echo ✓ Virtual environment created successfully
echo.

REM =============================================================================
REM STEP 3: ACTIVATE ENVIRONMENT AND INSTALL DEPENDENCIES
REM =============================================================================
echo [STEP 3/4] Installing Python dependencies...

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to activate virtual environment
    echo.
    echo RESOLUTION:
    echo 1. Check if venv\Scripts\activate.bat exists
    echo 2. Ensure no antivirus software is blocking the activation
    echo 3. Try running manually: venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

REM Upgrade pip to latest version for better dependency resolution
echo Upgrading pip to latest version...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to upgrade pip, continuing with current version...
    echo This may cause dependency installation issues.
    echo.
)

REM Install core AI/LLM dependencies
echo.
echo Installing AI and LangChain dependencies...
echo This may take several minutes depending on your internet connection...
echo.

REM Install LangChain and OpenAI packages
pip install langchain-openai==0.3.27
if %errorlevel% neq 0 (
    echo ERROR: Failed to install langchain-openai
    goto :installation_error
)

pip install langchain-core==0.3.68
if %errorlevel% neq 0 (
    echo ERROR: Failed to install langchain-core
    goto :installation_error
)

pip install openai==1.93.1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install openai
    goto :installation_error
)

pip install tiktoken==0.9.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install tiktoken
    goto :installation_error
)

echo ✓ AI dependencies installed successfully

REM Install configuration and utility dependencies
echo.
echo Installing configuration and utility dependencies...
pip install configparser python-dotenv
if %errorlevel% neq 0 (
    echo ERROR: Failed to install configuration dependencies
    goto :installation_error
)

echo ✓ Configuration dependencies installed

REM Install database connectivity dependencies
echo.
echo Installing database drivers...
echo Note: Some drivers may require additional system components
echo.

pip install pyodbc
if %errorlevel% neq 0 (
    echo WARNING: pyodbc installation failed
    echo This is needed for SQL Server connectivity
    echo You may need to install Visual C++ Build Tools
)

pip install mysql-connector-python
if %errorlevel% neq 0 (
    echo WARNING: mysql-connector-python installation failed
    echo This is needed for MySQL connectivity
)

pip install oracledb
if %errorlevel% neq 0 (
    echo WARNING: oracledb installation failed  
    echo This is needed for Oracle Database connectivity
)

echo ✓ Database drivers installation completed

REM Install file processing dependencies
echo.
echo Installing file processing dependencies...
pip install openpyxl pandas
if %errorlevel% neq 0 (
    echo ERROR: Failed to install file processing dependencies
    goto :installation_error
)

echo ✓ File processing dependencies installed

REM =============================================================================
REM STEP 4: VERIFY INSTALLATION
REM =============================================================================
echo.
echo [STEP 4/4] Verifying installation...

REM Test import of critical modules
python -c "import langchain_openai; print('✓ LangChain OpenAI')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ LangChain OpenAI import failed
    goto :verification_error
)

python -c "import openai; print('✓ OpenAI')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ OpenAI import failed
    goto :verification_error
)

python -c "import pandas; print('✓ Pandas')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Pandas import failed
    goto :verification_error
)

echo ✓ All critical modules imported successfully

REM =============================================================================
REM SETUP COMPLETION
REM =============================================================================
echo.
echo ========================================
echo ✓ Installation completed successfully! 
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. UPDATE API CREDENTIALS:
echo    Edit the .env file and replace 'temp' with your actual Azure OpenAI API key
echo.
echo 2. TEST YOUR SETUP:
echo    venv\Scripts\activate
echo    python test_setup.py
echo.
echo 3. RUN DEMO (No API key required):
echo    venv\Scripts\activate  
echo    python demo_scanner.py
echo.
echo 4. ANALYZE REAL DATA:
echo    venv\Scripts\activate
echo    python pii_scanner.py --ddl sample_schema.ddl
echo.
echo IMPORTANT NOTES:
echo - Always activate the virtual environment before running the scanner
echo - Keep your API credentials secure and never commit them to version control
echo - Run 'python test_setup.py' to validate your environment
echo.
echo GETTING AZURE OPENAI CREDENTIALS:
echo 1. Sign up for Azure at https://azure.microsoft.com/
echo 2. Create an Azure OpenAI resource
echo 3. Deploy a GPT-4 model
echo 4. Get your API key and endpoint from the Azure portal
echo 5. Update the .env file with your credentials
echo.
pause
goto :end

REM =============================================================================
REM ERROR HANDLERS
REM =============================================================================

:installation_error
echo.
echo ========================================
echo ✗ INSTALLATION ERROR
echo ========================================
echo.
echo A dependency installation failed. This can happen due to:
echo.
echo COMMON CAUSES:
echo - Network connectivity issues
echo - Missing system dependencies (Visual C++ Build Tools)
echo - Insufficient disk space
echo - Antivirus software interference
echo.
echo RESOLUTION STEPS:
echo 1. Check your internet connection
echo 2. Install Visual C++ Build Tools from:
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo 3. Temporarily disable antivirus during installation
echo 4. Free up disk space (need at least 1GB)
echo 5. Run this script as Administrator
echo.
echo MANUAL INSTALLATION:
echo If the automated installation continues to fail:
echo 1. Activate environment: venv\Scripts\activate
echo 2. Install manually: pip install -r requirements.txt
echo 3. Check for specific error messages
echo.
pause
exit /b 1

:verification_error
echo.
echo ========================================
echo ✗ VERIFICATION ERROR  
echo ========================================
echo.
echo Some packages were installed but cannot be imported.
echo This usually indicates:
echo.
echo POSSIBLE CAUSES:
echo - Incomplete package installation
echo - Python path issues
echo - Virtual environment activation problems
echo.
echo RESOLUTION:
echo 1. Ensure virtual environment is activated: venv\Scripts\activate
echo 2. Try reinstalling failed packages: pip install package_name --force-reinstall
echo 3. Check for error messages during import
echo.
pause
exit /b 1

:end
REM Script completed successfully
exit /b 0

REM =============================================================================
REM END OF SETUP SCRIPT
REM =============================================================================