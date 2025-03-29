import os
import shutil
import tempfile
import argparse
import glob
from moviepy import *
import PIL.Image
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import subprocess

def analyse_image(path):
    im = PIL.Image.open(path)
    results = {'size': im.size, 'mode': 'full'}
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region_dimensions = tile[1][2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results

def process_image(path, temp_dir):
    images = []
    mode = analyse_image(path)['mode']
    im = PIL.Image.open(path)
    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')
    
    try:
        while True:
            frame_file_name = os.path.join(temp_dir, f'{os.path.splitext(os.path.basename(path))[0]}-{i}.png')
            if '.gif' in path and not im.getpalette():
                im.putpalette(p)
            new_frame = PIL.Image.new('RGBA', im.size)
            if mode == 'partial':
                new_frame.paste(last_frame)
            new_frame.paste(im, (0, 0), im.convert('RGBA'))
            new_frame.save(frame_file_name, 'PNG')
            images.append(frame_file_name)
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return images

def interpolate_video(input_file, output_file, target_fps, mi_mode="mci", mc_mode="aobmc", scale=None, scale_width=None, scale_height=None):
    """
    Use ffmpeg to interpolate a video to a higher frame rate and optionally scale it.
    
    Args:
        input_file: Path to the input video file
        output_file: Path to save the interpolated video
        target_fps: Target frame rate for interpolation
        mi_mode: Motion interpolation mode (default: mci)
        mc_mode: Motion compensation mode (default: aobmc)
        scale: Float multiplier for both dimensions (e.g., 1.5 for 150% size)
        scale_width: Specific target width (overrides scale)
        scale_height: Specific target height (overrides scale)
        
    Note:
        This function requires ffmpeg to be installed on your system.
        If ffmpeg is not found, the function will fall back to the non-interpolated video.
    """
    # Build the filter string
    filters = []
    
    # Add scaling if requested
    if scale_width and scale_height:
        filters.append(f"scale={scale_width}:{scale_height}:flags=lanczos")
    elif scale:
        filters.append(f"scale=iw*{scale}:ih*{scale}:flags=lanczos")
        
    # Add interpolation
    filters.append(f"minterpolate=fps={target_fps}:mi_mode={mi_mode}:mc_mode={mc_mode}")
    
    # Combine filters
    filter_string = ",".join(filters)
    
    cmd = [
        "ffmpeg", "-y", "-i", input_file, 
        "-vf", filter_string,
        "-c:v", "libx264", "-c:a", "copy", output_file
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        scaling_msg = ""
        if scale:
            scaling_msg = f" and scaled by {scale}x"
        elif scale_width and scale_height:
            scaling_msg = f" and scaled to {scale_width}x{scale_height}"
        print(f"Successfully interpolated video to {target_fps} fps{scaling_msg}: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {e}")
        # If processing fails, copy the original file
        shutil.copy(input_file, output_file)
        print(f"Falling back to original version: {output_file}")
    except FileNotFoundError:
        print(f"Error: ffmpeg not found. Please install ffmpeg to use interpolation features.")
        # If ffmpeg is not found, copy the original file
        shutil.copy(input_file, output_file)
        print(f"Falling back to original version: {output_file}")

def webp_mp4(input_file, output_dir=None, fps=20, percentage=100, interpolate=False, target_fps=None, mi_mode="mci", mc_mode="aobmc", scale=None, scale_width=None, scale_height=None):
    temp_dir = tempfile.mkdtemp()
    try:
        images = process_image(input_file, temp_dir)
        if not images:
            print(f"No frames extracted from {input_file}")
            return []
        
        num_frames_part1 = int(len(images) * (percentage / 100))
        part1_images = images[:num_frames_part1]
        part2_images = images[num_frames_part1:] if num_frames_part1 < len(images) else []
        
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file1 = os.path.join(output_dir, f'{base_name}{"_part1" if part2_images else ""}.mp4')
            temp_output_file1 = os.path.join(temp_dir, f'{base_name}{"_part1" if part2_images else ""}_temp.mp4')
            output_file2 = os.path.join(output_dir, f'{base_name}_part2.mp4') if part2_images else None
            temp_output_file2 = os.path.join(temp_dir, f'{base_name}_part2_temp.mp4') if part2_images else None
        else:
            output_file1 = f'{base_name}{"_part1" if part2_images else ""}.mp4'
            temp_output_file1 = f'{os.path.join(temp_dir, base_name)}{"_part1" if part2_images else ""}_temp.mp4'
            output_file2 = f'{base_name}_part2.mp4' if part2_images else None
            temp_output_file2 = f'{os.path.join(temp_dir, base_name)}_part2_temp.mp4' if part2_images else None
        
        # Create initial video(s)
        clip1 = ImageSequenceClip(part1_images, fps=fps)
        clip1.write_videofile(temp_output_file1 if interpolate else output_file1, codec="libx264")
        
        # If interpolation is enabled, process the video with ffmpeg
        if interpolate:
            if target_fps is None:
                target_fps = fps * 2
            interpolate_video(temp_output_file1, output_file1, target_fps, mi_mode, mc_mode, scale, scale_width, scale_height)
            
        output_files = [output_file1]
        
        if part2_images:
            clip2 = ImageSequenceClip(part2_images, fps=fps)
            clip2.write_videofile(temp_output_file2 if interpolate else output_file2, codec="libx264")
            
            if interpolate:
                interpolate_video(temp_output_file2, output_file2, target_fps, mi_mode, mc_mode, scale, scale_width, scale_height)
                
            output_files.append(output_file2)
        
        return output_files
    finally:
        shutil.rmtree(temp_dir)

def combine_videos(output_files, output_file):
    if not output_files:
        print("No MP4 files found to combine.")
        return
    
    clips = [VideoFileClip(f) for f in sorted(output_files, key=lambda x: os.path.basename(x).lower())]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, codec="libx264")
    print(f"Combined video saved as {output_file}")

def process_file(input_file, output_dir, fps, percentage, interpolate=False, target_fps=None, mi_mode="mci", mc_mode="aobmc", scale=None, scale_width=None, scale_height=None):
    percentage_msg = f"({percentage}% in first file, {100 - percentage}% in second file)" if percentage != 100 else ""
    
    # Calculate actual target FPS for log message if interpolation is enabled
    display_fps = target_fps
    if interpolate and display_fps is None:
        display_fps = fps * 2
        
    # Build processing message
    processing_msg = []
    if interpolate:
        processing_msg.append(f"interpolation to {display_fps} fps")
    if scale:
        processing_msg.append(f"scaling by {scale}x")
    elif scale_width and scale_height:
        processing_msg.append(f"scaling to {scale_width}x{scale_height}")
        
    process_msg = f" with {' and '.join(processing_msg)}" if processing_msg else ""
    
    print(f"Processing: {input_file} {percentage_msg}{process_msg}")
    return webp_mp4(input_file, output_dir, fps, percentage, interpolate, target_fps, mi_mode, mc_mode, scale, scale_width, scale_height)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert WEBP files to MP4 and optionally combine them")
    parser.add_argument("input_files", nargs='*', help="Input file names (.webp)")
    parser.add_argument("-o", "--output_dir", help="Output directory (optional)")
    # Default fps is 20
    parser.add_argument("--fps", type=int, default=20, help="Frames per second for initial conversion (default: 20)")
    parser.add_argument("--percentage", type=int, default=100, help="Percentage of the video to process in the first file (default: 100%)")
    parser.add_argument("--combineoutput", help="Filename for combined output video (optional)")
    parser.add_argument("--threads", type=int, default=None, help="Number of threads to use (default: number of CPU cores)")
    # Interpolation options
    parser.add_argument("--interpolate", action="store_true", help="Enable frame interpolation using ffmpeg")
    parser.add_argument("--target_fps", type=int, default=None, help="Target FPS for interpolated video (default: 2x input fps)")
    parser.add_argument("--mi_mode", default="mci", choices=["mci", "blend", "dup"], 
                        help="Motion interpolation mode: mci (motion compensated), blend, or dup (duplicate) (default: mci)")
    parser.add_argument("--mc_mode", default="aobmc", 
                        choices=["obmc", "aobmc"], 
                        help="Motion compensation mode: obmc (Overlapped Block) or aobmc (Adaptive Overlapped Block) (default: aobmc)")
    # Scaling options
    parser.add_argument("--scale", type=float, help="Scale factor for video dimensions (e.g., 1.5 for 150% size)")
    parser.add_argument("--scale_width", type=int, help="Target width for scaling (overrides --scale)")
    parser.add_argument("--scale_height", type=int, help="Target height for scaling (overrides --scale)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    input_files = args.input_files if args.input_files else glob.glob("*.webp")
    
    if not input_files:
        print("No WEBP files found in the current directory.")
        exit()
    
    # Use number of CPU cores if threads not specified
    num_threads = args.threads or multiprocessing.cpu_count()
    print(f"Using {num_threads} threads for parallel processing")
    
    all_output_files = []
    
    # Process files in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Create a list of futures for each file
        futures = [
            executor.submit(process_file, 
                          input_file, 
                          args.output_dir, 
                          args.fps, 
                          args.percentage,
                          args.interpolate,
                          args.target_fps,
                          args.mi_mode,
                          args.mc_mode,
                          args.scale,
                          args.scale_width,
                          args.scale_height)
            for input_file in input_files
        ]
        
        # Collect results as they complete
        for future in futures:
            try:
                output_files = future.result()
                all_output_files.extend(output_files)
            except Exception as e:
                print(f"Error processing file: {e}")
    
    if args.combineoutput and all_output_files:
        combine_videos(all_output_files, args.combineoutput)
