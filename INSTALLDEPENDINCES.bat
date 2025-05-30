@echo off
REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found. Downloading and installing Python 3.12.3...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python-installer.exe
    echo Python installed. Please restart this script if you see errors below.
)

REM Install Python dependencies for the 3D engine
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pause 