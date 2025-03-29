#!/bin/bash

echo "WebP to MP4 Converter with Frame Interpolation and Upscaling"
echo "Place your WebP files in this folder and run this script."
echo

# Check if any WebP files exist in the current directory
if ! ls *.webp 1> /dev/null 2>&1; then
    echo "No WebP files found in the current directory!"
    echo "Please place your WebP files in this folder and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

# Use 1.5x scaling factor to maintain aspect ratio
python3 videoconvert.py --fps 16 --interpolate --target_fps 32 --mi_mode mci --mc_mode aobmc --scale 1.5

echo
echo "Conversion complete! Press Enter to exit..."
read 