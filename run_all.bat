@echo off
echo ========================================================
echo Launching SAKSHYA Full Stack (Backend + Frontend)
echo ========================================================
start "SAKSHYA Backend" cmd /c "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "SAKSHYA Frontend" cmd /c "%~dp0run_frontend.bat"
echo.
echo Backend URL:  http://127.0.0.1:8000/docs
echo Frontend URL: http://localhost:3000
echo.
echo Both services are starting in separate windows.
pause
