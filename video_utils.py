import os
import sys
import subprocess
import glob

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as normal python script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_exe = os.path.join(base_path, "ProjectFiles", "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe):
        return ffmpeg_exe
    return None

def extract_thumbnails(src_dir, frame_number=1, progress_callback=None):
    videos_dir = os.path.join(src_dir, "Videos")
    if not os.path.exists(videos_dir):
        return False
        
    thumbs_dir = os.path.join(src_dir, "VideoThumbs")
    os.makedirs(thumbs_dir, exist_ok=True)
    
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("FFmpeg not found!")
        return False
        
    # Get all video files
    extensions = ('*.mp4', '*.mov', '*.avi', '*.mkv', '*.wmv')
    video_files = []
    for ext in extensions:
        video_files.extend(glob.glob(os.path.join(videos_dir, ext)))
        video_files.extend(glob.glob(os.path.join(videos_dir, ext.upper())))
        
    total_videos = len(video_files)
    if total_videos == 0:
        return False
        
    for idx, video_path in enumerate(video_files):
        video_filename = os.path.basename(video_path)
        base_name, _ = os.path.splitext(video_filename)
        thumb_path = os.path.join(thumbs_dir, f"{base_name}.jpg")
        
        if not os.path.exists(thumb_path):
            # Calculate the timestamp to extract if it's based on frames
            # A common trick to get the nth frame without knowing fps perfectly is to use select=eq(n\,X)
            # -vframes 1 ensures only 1 frame is output
            # For 0-indexed frame numbers, frame 1 is n=0
            target_n = max(0, frame_number - 1)
            
            cmd = [
                ffmpeg_path,
                "-y",  # Overwrite output files without asking
                "-i", video_path,
                "-vf", f"select=eq(n\\,{target_n})",
                "-fps_mode", "vfr",
                "-update", "1",
                "-vframes", "1",
                "-q:v", "2", # High quality JPEG
                thumb_path
            ]
            
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            except Exception as e:
                print(f"Failed to extract frame from {video_filename}: {e}")
                
        if progress_callback:
            progress_callback(int(((idx + 1) / total_videos) * 100))
            
    return True
