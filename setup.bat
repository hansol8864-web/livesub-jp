@echo off
cd /d "%~dp0"

echo.
echo ====================================
echo   jp-translator - Setup
echo ====================================
echo.

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python not found in PATH.
    echo Install from python.org and check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo venv folder exists, removing old one...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERROR: venv creation failed.
    pause
    exit /b 1
)

echo.
echo [3/5] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: pip upgrade failed.
    pause
    exit /b 1
)

echo.
echo [4/5] Installing packages (3-10 minutes)...
venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package install failed. See messages above.
    echo If wheels are missing for Python 3.14, install Python 3.12
    echo from python.org and re-run setup.bat.
    pause
    exit /b 1
)

echo.
echo [5/5] Downloading Whisper "small" model (~500MB)...
venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; m = WhisperModel('small', device='cpu', compute_type='int8'); print('Model OK')"
if errorlevel 1 (
    echo ERROR: Whisper model download failed.
    pause
    exit /b 1
)

echo.
echo ====================================
echo   Setup complete!
echo   Now double-click run.bat
echo ====================================
pause
