@echo off
echo WebP to MP4 Converter with Frame Interpolation (No Upscaling)
echo Place your WebP files in this folder and run this batch file.
echo.

REM Check for WebP files
if not exist *.webp (
    echo No WebP files found in the current directory!
    echo Please place your WebP files in this folder and try again.
    pause
    exit /b
)

REM Run the conversion
python videoconvert.py --fps 16 --interpolate --target_fps 32

echo.
echo Conversion complete! Press any key to exit.
pause 