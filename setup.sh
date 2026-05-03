#!/bin/bash
# Quick Start Script

echo "🚀 Starting Secure Enterprise Dashboard..."
echo ""

# Check Python
echo "✓ Checking Python..."
python --version

# Check Node.js
echo "✓ Checking Node.js..."
node --version

echo ""
echo "📦 Setting up Backend..."
cd backend
python -m venv venv

# Activate venv
source venv/bin/activate || venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

echo "✓ Backend dependencies installed"
echo ""

echo "📦 Setting up Frontend..."
cd ../frontend
npm install
echo "✓ Frontend dependencies installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Terminal 1 (Backend): cd backend && source venv/bin/activate && python main.py"
echo "2. Terminal 2 (Frontend): cd frontend && npm start"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo ""
echo "Test Credentials:"
echo "  Employee: employee / employee123"
echo "  Manager:  manager / manager123"
echo "  Admin:    admin / admin123"
