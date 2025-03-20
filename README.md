# webptomp4
**Webp to mp4 video converter**

A fast, multithreaded converter for webp animations to mp4 format. Works on any OS that supports Python3 (Windows, macOS, Linux).

## Features

- Multithreaded processing for faster conversion
- Support for batch processing
- Automatic CPU core detection
- Split video into parts based on percentage
- Combine multiple videos into one
- Cross-platform compatibility

## Requirements

- Python3
- Required Python packages:
  - Pillow
  - Moviepy
  - Argparse
  - Glob2

## Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3
pip3 install moviepy pillow argparse glob2
```

### macOS
```bash
brew install python3  # If you don't have Python installed
pip3 install moviepy pillow argparse glob2
```

### Windows
```bash
winget install python3
pip3 install moviepy pillow argparse glob2
```

## Usage

Place `videoconvert.py` in the same folder as your webp files.

### Basic Usage
```bash
python3 videoconvert.py  # Converts all webp files with default settings (20 fps)
python3 videoconvert.py --fps 16  # Set custom frame rate
```

### Advanced Options
```bash
# Use specific number of threads
python3 videoconvert.py --threads 4

# Split video into two parts (80% and 20%)
python3 videoconvert.py --percentage 80

# Combine all converted videos into one file
python3 videoconvert.py --combineoutput final.mp4

# Specify output directory
python3 videoconvert.py -o output_folder

# Process specific files
python3 videoconvert.py file1.webp file2.webp
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--fps` | Frames per second | 20 |
| `--threads` | Number of parallel conversions | Number of CPU cores |
| `--percentage` | Split video into two parts | 100 |
| `--combineoutput` | Output filename for combined video | None |
| `-o, --output_dir` | Output directory | Current directory |

## Examples

### Convert all webp files in folder
```bash
python3 videoconvert.py
```
![percentage](./images/image_normal.png)

### Split video into two parts
```bash
python3 videoconvert.py --percentage 80
```
![percentage](./images/image_prosent.png)

### Combine multiple videos
```bash
python3 videoconvert.py --combineoutput final.mp4
```
![combine](./images/image_combine.png)

## Notes

- Videos are sorted by filename (a-z, 1-9) when combining
- Combining videos may fail if they have different resolutions
- For best performance, the number of threads will automatically match your CPU cores
- Temporary files are automatically cleaned up after conversion

## Roadmap

Future improvements planned:

1. Performance Improvements:
   - GPU acceleration support
   - Frame skipping for preview generation
   - Memory management for large files

2. Feature Enhancements:
   - Support for more output formats (AVI, MOV)
   - Video quality settings and compression options
   - Custom frame selection
   - Progress bars

3. User Experience:
   - GUI interface
   - Drag and drop support
   - Preview window
   - Estimated time remaining

4. Error Handling:
   - Better error messages and logging
   - Automatic recovery from failed conversions
   - Checksum verification

5. Integration:
   - Watch folder functionality
   - Webhook support
   - Cloud storage integration
   - Command line completion
