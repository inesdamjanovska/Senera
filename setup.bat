@echo off
echo 🚀 Senera Fashion AI - Environment Setup
echo =======================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo Starting setup process...
python setup.py

echo.
echo 💡 Setup complete! Remember to:
echo 1. Update backend/.env with your OpenAI API key
echo 2. Start backend: cd backend && python app.py
echo 3. Start mobile app: cd SeneraMobile && npm start
echo.
pause
