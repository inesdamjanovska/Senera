@echo off
echo 🔄 Updating IP addresses automatically...
echo.

cd /d "%~dp0"
python update_ip.py

echo.
echo 💡 Tip: You can also run this script anytime your IP changes!
echo.
pause
