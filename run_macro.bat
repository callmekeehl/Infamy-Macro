@echo off
TITLE GPO Sett's Arena Infamy Macro Launcher
cd /d "%~dp0"

echo ===============================================
echo   GPO Sett's Arena Infamy Macro Launcher
echo ===============================================
echo.
echo Installing/checking Python dependencies...
python -m pip install -r requirements.txt

echo.
echo Launching Macro GUI...
python gui_app.py
pause
