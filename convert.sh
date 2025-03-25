#!/bin/bash

echo "WebM to MP4 Converter with Frame Interpolation"
echo "Place your WebM files in this folder and run this script."
echo

# Check if any WebM files exist in the current directory
if ! ls *.webm 1> /dev/null 2>&1; then
    echo "No WebM files found in the current directory!"
    echo "Please place your WebM files in this folder and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

python3 videoconvert.py --fps 16 --interpolate --target_fps 32 --mi_mode mci --mc_mode aobmc

echo
echo "Conversion complete! Press Enter to exit..."
read 