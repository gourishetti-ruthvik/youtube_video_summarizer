@echo off
REM Startup script for YouTube Video Summarizer (Windows)

echo ================================
echo YouTube Video Summarizer
echo ================================
echo.

REM Check if GEMINI_API_KEY is set
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY is not set!
    echo.
    echo Please set your Gemini API key:
    echo   set GEMINI_API_KEY=your_key_here
    echo.
    echo Get your key from: https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

echo Starting Flask Backend...
echo.
start cmd /k "python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Streamlit Frontend...
echo.
start cmd /k "streamlit run streamlit_app.py"

echo.
echo Both services are starting...
echo Backend: http://127.0.0.1:5000
echo Frontend: http://localhost:8501
echo.
echo Keep both terminal windows open while using the app.
echo.
pause
