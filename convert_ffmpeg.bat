@echo off
echo WebP to MP4 Converter with Frame Interpolation
echo.

REM Set path to the ffmpeg executable
set "PATH=%PATH%;%CD%\ffmpeg-7.1.1-essentials_build\bin"
echo FFmpeg path set to: %CD%\ffmpeg-7.1.1-essentials_build\bin

REM Verify FFmpeg is accessible
where ffmpeg
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: FFmpeg not found in PATH
    pause
    exit /b
)

echo FFmpeg found! Running conversion...
echo.

REM Start conversion
python videoconvert.py --fps 16 --interpolate --target_fps 32

echo.
echo Conversion complete! Press any key to exit.
pause 