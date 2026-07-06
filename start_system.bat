@echo off
echo ========================================================
echo Starting AI Market Analytics System...
echo ========================================================

echo 1. Starting FastAPI Backend Server (Port 8000)...
start "FastAPI Backend" cmd /k "cd /d %~dp0ai-engine && venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"

echo 2. Starting Celery Worker (Live AI Predictions)...
start "Celery Worker" cmd /k "cd /d %~dp0ai-engine && venv\Scripts\celery.exe -A app.worker.tasks worker --pool=solo --loglevel=info"

echo 3. Starting Celery Beat (5-min Scheduler)...
start "Celery Beat" cmd /k "cd /d %~dp0ai-engine && venv\Scripts\celery.exe -A app.worker.tasks beat --loglevel=info"

echo 4. Starting Next.js Frontend (Port 3000)...
start "Next.js Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo All services are starting in separate windows!
echo Once they are ready, open your browser and go to:
echo http://localhost:3000
echo.
pause
