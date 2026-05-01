@echo off
cd /d "%~dp0"

echo.
echo ====================================
echo   LiveSubJP - Build .exe
echo ====================================
echo.

if not exist "venv\Scripts\pyinstaller.exe" (
    echo ERROR: PyInstaller not found in venv. Run setup.bat first.
    pause
    exit /b 1
)

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist LiveSubJP.spec del LiveSubJP.spec

echo.
echo Building (10-15 min)...
venv\Scripts\pyinstaller.exe ^
    --name LiveSubJP ^
    --icon=icon.ico ^
    --collect-all faster_whisper ^
    --collect-all ctranslate2 ^
    --collect-all pyaudiowpatch ^
    --collect-all deep_translator ^
    --collect-all silero_vad ^
    --collect-all onnxruntime ^
    --add-data "icon.ico;." ^
    --noconfirm ^
    --console ^
    main.py

if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ====================================
echo   Build complete: dist\LiveSubJP\
echo ====================================
pause
