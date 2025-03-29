#!/bin/bash

echo "WebP Cleanup Script"
echo "This script will remove .webp files that have already been converted to .mp4"
echo

# Array to store files to be deleted
declare -a to_delete=()

# Find files to be deleted
echo "The following .webp files have been converted and can be deleted:"
echo "-----------------------------------------------------------"
for webp in *.webp; do
    # Check if the file exists (in case no .webp files are found)
    if [ -f "$webp" ]; then
        # Get the corresponding mp4 filename
        mp4="${webp%.webp}.mp4"
        
        # Check if the mp4 exists and is not empty
        if [ -f "$mp4" ] && [ -s "$mp4" ]; then
            echo "- $webp"
            to_delete+=("$webp")
        fi
    fi
done

# Check if any files were found
if [ ${#to_delete[@]} -eq 0 ]; then
    echo "No converted files found to clean up."
    exit 0
fi

echo
echo "Total files to be deleted: ${#to_delete[@]}"
echo

# Ask for confirmation
read -p "Do you want to proceed with deletion? (y/N) " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    # Counter for deleted files
    deleted=0
    
    # Delete the files
    for webp in "${to_delete[@]}"; do
        echo "Removing $webp"
        rm "$webp"
        ((deleted++))
    done
    
    echo
    echo "Cleanup complete! Removed $deleted file(s)."
else
    echo "Operation cancelled. No files were deleted."
fi

# If running from Windows, keep the window open
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo
    read -p "Press Enter to exit..."
fi 