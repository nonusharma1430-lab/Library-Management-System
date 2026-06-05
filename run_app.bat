@echo off
echo Starting Library Management System...
echo.

echo Testing MongoDB connection...
python test_connection.py
if errorlevel 1 (
    echo.
    echo Please fix MongoDB connection before running the app.
    pause
    exit /b 1
)

echo.
echo Starting Flask application...
python app.py

pause