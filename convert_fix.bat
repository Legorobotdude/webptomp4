@echo off
echo WebP to MP4 Converter with Frame Interpolation
echo.

REM Check if FFmpeg is directly accessible
where ffmpeg >nul 2>nul
if %ERRORLEVEL% EQU 0 goto :run_script

REM Look for FFmpeg in the extracted directory
set FFMPEG_PATH=
if exist "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" (
    set "FFMPEG_PATH=%CD%\ffmpeg-master-latest-win64-gpl\bin"
    goto :found_ffmpeg
)

REM Check common installation paths
for %%i in (
    "C:\Program Files\ffmpeg\bin"
    "C:\Program Files (x86)\ffmpeg\bin"
    "C:\ffmpeg\bin"
    "%PROGRAMFILES%\FFmpeg\bin"
    "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
) do (
    if exist "%%~i\ffmpeg.exe" (
        set "FFMPEG_PATH=%%~i"
        goto :found_ffmpeg
    )
)

:not_found
echo FFmpeg not found. The interpolation will not work.
echo Would you like to continue anyway? (Y/N)
set /p choice=
if /i "%choice%"=="Y" goto :run_script
exit /b

:found_ffmpeg
echo Found FFmpeg at: %FFMPEG_PATH%
set "PATH=%PATH%;%FFMPEG_PATH%"
echo Added FFmpeg to PATH

:run_script
echo Running conversion...
echo.

REM Start conversion
python videoconvert.py --fps 16 --interpolate --target_fps 32

echo.
echo Conversion complete! Press any key to exit.
pause 