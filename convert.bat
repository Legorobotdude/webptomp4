@echo off
echo WebM to MP4 Converter with Frame Interpolation
echo Place your WebM files in this folder and run this batch file.
echo.

if not exist *.webm (
    echo No WebM files found in the current directory!
    echo Please place your WebM files in this folder and try again.
    pause
    exit /b
)

python videoconvert.py --fps 16 --interpolate --target_fps 32 --mi_mode mci --mc_mode aobmc

echo.
echo Conversion complete! Press any key to exit.
pause 