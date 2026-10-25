@echo off
echo ========================================================
echo Starting SAKSHYA FastAPI Backend on http://127.0.0.1:8000
echo ========================================================
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
python -m uvicorn api.gateway:app --port 8000 --reload
pause
