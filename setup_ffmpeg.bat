@echo off
echo Setting up FFmpeg for WebP to MP4 conversion...
echo.

REM Check if FFmpeg is already installed
where ffmpeg >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo FFmpeg is already installed and available in your PATH.
    goto :end
)

echo Downloading FFmpeg...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"

echo Extracting FFmpeg...
powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force}"

echo Adding FFmpeg to system PATH temporarily...
set PATH=%PATH%;%CD%\ffmpeg-master-latest-win64-gpl\bin

echo Testing FFmpeg installation...
ffmpeg -version

echo.
echo FFmpeg has been set up successfully!
echo To make this permanent, please add the following path to your system PATH:
echo %CD%\ffmpeg-master-latest-win64-gpl\bin
echo.

:end
echo Press any key to exit...
pause 