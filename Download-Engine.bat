@echo off
echo Downloading Shitty-3d-Engine ZIP from GitHub...
powershell -Command "Invoke-WebRequest -Uri 'https://codeload.github.com/Roms-lab/Shitty-3d-Engine/zip/refs/heads/main' -OutFile 'Shitty-3d-Engine-main.zip'"
echo Download finished.
pause
