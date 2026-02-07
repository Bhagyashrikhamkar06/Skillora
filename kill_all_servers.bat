@echo off
echo ============================================================
echo SKILLORA - Kill All Servers and Restart Clean
echo ============================================================
echo.

echo Step 1: Killing all Python processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Killed Python processes
) else (
    echo ℹ No Python processes found
)

echo.
echo Step 2: Waiting for ports to free up...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Verifying ports are free...
netstat -ano | findstr :5000
if %errorlevel% equ 0 (
    echo ⚠ Port 5000 still in use!
) else (
    echo ✓ Port 5000 is free
)

netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo ⚠ Port 8000 still in use!
) else (
    echo ✓ Port 8000 is free
)

echo.
echo ============================================================
echo All servers stopped. Now start them manually:
echo.
echo Terminal 1 (Backend):
echo   cd C:\Users\bhagy\OneDrive\Desktop\Skillora\backend
echo   python app.py
echo.
echo Terminal 2 (Frontend):
echo   cd C:\Users\bhagy\OneDrive\Desktop\Skillora\frontend
echo   python -m http.server 8000
echo ============================================================
pause
