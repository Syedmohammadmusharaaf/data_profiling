# 🚀 Quick Installation Guide

## Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **MongoDB 5.0+** (optional - can run without for basic testing)

## 🏃‍♂️ Quick Start (Windows)

1. **Download and extract** the project files
2. **Run PowerShell as Administrator** 
3. **Navigate to project directory:**
   ```powershell
   cd path\to\pii-scanner
   ```
4. **Execute startup script:**
   ```powershell
   .\start_services.ps1
   ```
5. **Open browser** and go to `http://localhost:3000`

## 🏃‍♂️ Quick Start (Linux/macOS)

1. **Download and extract** the project files
2. **Open terminal**
3. **Navigate to project directory:**
   ```bash
   cd path/to/pii-scanner
   ```
4. **Make script executable and run:**
   ```bash
   chmod +x start_services.sh
   ./start_services.sh
   ```
5. **Open browser** and go to `http://localhost:3000`

## 📋 Manual Installation

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install    # or yarn install
npm run dev    # or yarn dev
```

## 🔧 Troubleshooting

- **Port conflicts**: Kill processes using ports 3000 and 8001
- **Permission errors**: Run as administrator/sudo
- **Missing dependencies**: Install Python/Node.js from official websites
- **MongoDB issues**: The app works without MongoDB for basic testing

## 📞 Need Help?

Check the main [README.md](README.md) for detailed documentation.