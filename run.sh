#!/bin/bash
# Startup script for YouTube Video Summarizer (Linux/Mac)

echo "================================"
echo "YouTube Video Summarizer"
echo "================================"
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY is not set!"
    echo ""
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY='your_key_here'"
    echo ""
    echo "Get your key from: https://aistudio.google.com/app/apikey"
    echo ""
    exit 1
fi

echo "Starting Flask Backend..."
echo ""
python app.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

echo "Starting Streamlit Frontend..."
echo ""
streamlit run streamlit_app.py &
FRONTEND_PID=$!

echo ""
echo "Both services are running..."
echo "Backend: http://127.0.0.1:5000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:8501 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
