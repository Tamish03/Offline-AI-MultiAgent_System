@echo off
title AI OS Launcher
color 0B

:: Force working directory to the folder containing this script
cd /d "%~dp0"

echo ===================================================
echo               STARTING OFFLINE AI OS
echo ===================================================
echo.

:: Detect python executable to use
set "PYTHON_EXE=python"
if exist "venv\Scripts\python.exe" (
    echo [INFO] Virtual environment detected.
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    echo [WARN] Virtual environment venv not found. Using system python.
)

:: Verify python is available
if "%PYTHON_EXE%"=="python" goto verify_system_python
goto verify_venv_python

:verify_system_python
where python >nul 2>&1
if errorlevel 1 goto err_system_python
goto check_ollama

:verify_venv_python
if not exist "%PYTHON_EXE%" goto err_venv_python
goto check_ollama

:err_system_python
color 0C
echo [ERROR] Python is not installed or not in PATH!
echo Please install Python to run the AI OS.
pause
exit /b

:err_venv_python
color 0C
echo [ERROR] Virtual environment python.exe not found at:
echo "%PYTHON_EXE%"
pause
exit /b

:check_ollama
:: Check if Ollama is running
echo [INFO] Checking if Ollama is running...
curl -s -I http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama does not seem to be running at http://localhost:11434.
    echo Please start Ollama to ensure local models can process queries.
    echo.
) else (
    echo [OK] Ollama is active.
)

:: Launch the server and queue runner in separate windows using the correct python executable
echo [INFO] Starting web server...
start "AI OS Server" cmd /k ""%PYTHON_EXE%" dashboard.py"

echo [INFO] Starting background workflow runner...
start "AI OS Runner" cmd /k ""%PYTHON_EXE%" run_ai_os.py"

:: Wait for the server to start (2 seconds)
echo [INFO] Waiting for server to initialize...
ping 127.0.0.1 -n 3 >nul

:: Open browser
echo [INFO] Launching dashboard in your browser...
start http://localhost:8000

echo.
echo ===================================================
echo   AI OS IS RUNNING AT: http://localhost:8000
echo   To stop the server, close the "AI OS Server" terminal window.
echo ===================================================
echo.
pause
