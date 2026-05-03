@echo off
REM Quick Start Script for Windows

echo 🚀 Starting Secure Enterprise Dashboard...
echo.

echo ✓ Checking Python...
python --version

echo ✓ Checking Node.js...
node --version

echo.
echo 📦 Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo ✓ Backend dependencies installed

echo.
echo 📦 Setting up Frontend...
cd ..\frontend
npm install
echo ✓ Frontend dependencies installed

echo.
echo ✅ Setup complete!
echo.
echo To start the application:
echo 1. Terminal 1 (Backend): cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo 2. Terminal 2 (Frontend): cd frontend ^&^& npm start
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo Test Credentials:
echo   Employee: employee / employee123
echo   Manager:  manager / manager123
echo   Admin:    admin / admin123

pause
