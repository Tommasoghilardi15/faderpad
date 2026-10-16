@echo off
rem Builds dist\Faderpad.exe on your own PC. Double-click it from the project folder.
cd /d "%~dp0"
echo Installing build tools...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed

echo.
echo Building Faderpad.exe...
python -m PyInstaller --noconfirm --clean faderpad.spec
if errorlevel 1 goto failed

echo.
echo Done: %~dp0dist\Faderpad.exe
pause
exit /b 0

:failed
echo.
echo Build failed. The messages above say why.
pause
exit /b 1
