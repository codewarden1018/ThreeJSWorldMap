@echo off
echo ============================================================
echo Starting Interactive Globe Server
echo ============================================================
echo.
echo Server will start at: http://localhost:5000
echo.
echo IMPORTANT: Keep this window open to see console debug messages
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python app_sqlite.py

pause
