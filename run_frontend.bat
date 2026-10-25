@echo off
echo ========================================================
echo Starting SAKSHYA Next.js Frontend on http://localhost:3000
echo ========================================================
cd /d "%~dp0frontend"
npm run dev -- -p 3000
pause
