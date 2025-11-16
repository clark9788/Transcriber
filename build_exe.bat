@echo off
echo Building Medical Transcriber executable...
echo.

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r Transcriber\requirements.txt
pip install pyinstaller

REM Build executable
echo.
echo Building executable...
pyinstaller --name="MedicalTranscriber" ^
    --onefile ^
    --windowed ^
    --add-data "Transcriber\templates;templates" ^
    --hidden-import=google.cloud.speech ^
    --hidden-import=google.cloud.storage ^
    --hidden-import=sounddevice ^
    --hidden-import=soundfile ^
    --icon=NONE ^
    Transcriber\main.py

echo.
echo Build complete! Check the 'dist' folder for MedicalTranscriber.exe
pause

