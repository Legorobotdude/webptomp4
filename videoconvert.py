import os
import shutil
import tempfile
import argparse
import glob
from moviepy import *
import PIL.Image

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

def webp_mp4(input_file, output_dir=None, fps=20, percentage=100):
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
            output_file1 = os.path.join(output_dir, f'{base_name}_part1.mp4')
            output_file2 = os.path.join(output_dir, f'{base_name}_part2.mp4') if part2_images else None
        else:
            output_file1 = f'{base_name}_part1.mp4'
            output_file2 = f'{base_name}_part2.mp4' if part2_images else None
        
        clip1 = ImageSequenceClip(part1_images, fps=fps)
        clip1.write_videofile(output_file1, codec="libx264")
        
        output_files = [output_file1]
        
        if part2_images:
            clip2 = ImageSequenceClip(part2_images, fps=fps)
            clip2.write_videofile(output_file2, codec="libx264")
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

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert WEBP files to MP4 and optionally combine them")
    parser.add_argument("input_files", nargs='*', help="Input file names (.webp)")
    parser.add_argument("-o", "--output_dir", help="Output directory (optional)")
    parser.add_argument("--fps", type=int, default=20, help="Frames per second (default: 20)")
    parser.add_argument("--percentage", type=int, default=100, help="Percentage of the video to process in the first file (default: 100%)")
    parser.add_argument("--combineoutput", help="Filename for combined output video (optional)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    input_files = args.input_files if args.input_files else glob.glob("*.webp")
    
    if not input_files:
        print("No WEBP files found in the current directory.")
        exit()
    
    all_output_files = []
    
    for input_file in input_files:
        print(f"Processing: {input_file} ({args.percentage}% in first file, {100 - args.percentage}% in second file)")
        output_files = webp_mp4(input_file, args.output_dir, args.fps, args.percentage)
        all_output_files.extend(output_files)
    
    if args.combineoutput and all_output_files:
        combine_videos(all_output_files, args.combineoutput)
