# ffmpeg_composer.py
# Assembles final video using FFmpeg filter_complex for professional multi-layer compositing

import subprocess
import os
import json


def get_video_duration(video_path: str) -> float | None:
    """Get duration of a video file in seconds using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return duration
    except Exception as e:
        print(f"⚠️  Could not get video duration: {e}")
        return None


def compose_video_with_ffmpeg(
    background_video: str,
    screenshot_image: str,
    subtitle_file: str,
    audio_file: str,
    output_file: str = "final_short.mp4",
    target_width: int = 1080,
    target_height: int = 1920,
    screenshot_position: str = "top",
    screenshot_scale: float = 0.9
) -> str | None:
    """
    Compose final Shorts video using FFmpeg filter_complex.
    
    This is the professional approach from the Turkish specification:
    - Scale/crop background to 9:16 (1080x1920)
    - Overlay screenshot image at top
    - Burn subtitles at bottom
    - Add audio track
    - Use -shortest to match audio duration
    
    Args:
        background_video: Path to Pexels background video
        screenshot_image: Path to Reddit screenshot PNG
        subtitle_file: Path to .srt subtitle file
        audio_file: Path to audio file (with 1.3x speed)
        output_file: Output video path
        target_width: Output width (1080 for Shorts)
        target_height: Output height (1920 for Shorts)
        screenshot_position: "top", "center", or "bottom"
        screenshot_scale: Scale factor for screenshot (0.9 = 90% of width)
        
    Returns:
        Path to output file or None on failure
    """
    print("🎬 Composing video with FFmpeg filter_complex...")
    print(f"   Background: {background_video}")
    print(f"   Screenshot: {screenshot_image}")
    print(f"   Subtitles: {subtitle_file}")
    print(f"   Audio: {audio_file}")
    
    # Check if required files exist
    for file, name in [(background_video, "Background"), (screenshot_image, "Screenshot"), 
                        (audio_file, "Audio")]:
        if not os.path.exists(file):
            print(f"❌ {name} file not found: {file}")
            return None
    
    # Check subtitle file if provided
    if subtitle_file and not os.path.exists(subtitle_file):
        print(f"❌ Subtitle file not found: {subtitle_file}")
        return None
    
    # Calculate screenshot overlay dimensions
    screenshot_width = int(target_width * screenshot_scale)
    
    # Calculate Y position based on position preference
    if screenshot_position == "top":
        screenshot_y = 50  # 50 pixels from top
    elif screenshot_position == "center":
        screenshot_y = f"(H-h)/2"  # Centered
    elif screenshot_position == "bottom":
        screenshot_y = f"H-h-300"  # 300 pixels from bottom (leave room for subtitles)
    else:
        screenshot_y = 50  # Default to top
    
    # Build FFmpeg filter_complex command
    # 
    # Filter chain explained:
    # [0:v] = background video input
    # 1. scale/crop to 9:16 (1080x1920) - crop from center
    # 2. overlay screenshot image at calculated position
    # 3. burn subtitles at bottom with styling (if provided)
    # 4. output as [outv]
    # [2:a] = audio input (already sped up)
    
    # Build filter chain
    filter_parts = []
    
    # Step 1: Scale and crop background to 9:16
    filter_parts.append(
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height}[bg]"
    )
    
    # Step 2: Prepare screenshot - scale to fit width
    filter_parts.append(f"[1:v]scale={screenshot_width}:-1[screenshot]")
    
    # Step 3: Overlay screenshot on background
    if subtitle_file:
        # If we have subtitles, output to intermediate stream for subtitle burning
        filter_parts.append(f"[bg][screenshot]overlay=(W-w)/2:{screenshot_y}[videowithshot]")
        
        # Step 4: Burn subtitles with styling
        subtitle_escaped = subtitle_file.replace("\\", "\\\\").replace(":", "\\:")
        filter_parts.append(
            f"[videowithshot]subtitles='{subtitle_escaped}'"
            f":force_style='FontName=Arial Bold,FontSize=24,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=0,"
            f"Alignment=2,MarginV=100'[outv]"
        )
    else:
        # No subtitles - output directly
        filter_parts.append(f"[bg][screenshot]overlay=(W-w)/2:{screenshot_y}[outv]")
    
    filter_complex = "; ".join(filter_parts)
    
    # Build full FFmpeg command
    command = [
        "ffmpeg",
        "-i", background_video,           # Input 0: background video
        "-i", screenshot_image,           # Input 1: screenshot image
        "-i", audio_file,                 # Input 2: audio
        "-filter_complex", filter_complex,
        "-map", "[outv]",                 # Map filtered video
        "-map", "2:a",                    # Map audio from input 2
        "-c:v", "libx264",                # H.264 video codec
        "-preset", "medium",              # Encoding speed/quality balance
        "-crf", "23",                     # Quality (18-28, lower = better)
        "-c:a", "aac",                    # AAC audio codec
        "-b:a", "192k",                   # Audio bitrate
        "-shortest",                      # Stop when shortest stream ends (audio)
        "-y",                             # Overwrite output
        output_file
    ]
    
    print("\n📋 FFmpeg command:")
    print(" ".join(command))
    print()
    
    try:
        # Run FFmpeg
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Video composed successfully: {output_file}")
        
        # Get output file size
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"   File size: {size_mb:.2f} MB")
        
        # Get output duration
        duration = get_video_duration(output_file)
        if duration:
            print(f"   Duration: {duration:.2f} seconds")
        
        return output_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
        print("\nSTDERR:")
        print(e.stderr)
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def compose_video_simple(
    background_video: str,
    audio_file: str,
    output_file: str = "simple_short.mp4"
) -> str | None:
    """
    Simplified version - just combines background video with audio.
    Useful for testing or minimal videos.
    """
    print("🎬 Simple video composition (background + audio only)...")
    
    command = [
        "ffmpeg",
        "-i", background_video,
        "-i", audio_file,
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        "-shortest",
        "-y",
        output_file
    ]
    
    try:
        subprocess.run(command, capture_output=True, check=True)
        print(f"✅ Simple video created: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("Testing FFmpeg compositor...")
    print("\n⚠️  This test requires actual video/audio/subtitle files.")
    print("To test manually, run:")
    print()
    print("  python ffmpeg_composer.py")
    print()
    print("With test files named:")
    print("  - background.mp4 (Pexels video)")
    print("  - post.png (Reddit screenshot)")
    print("  - subtitles.srt (edge-tts subtitles)")
    print("  - audio.mp3 (edge-tts audio)")
    
    # Check if test files exist
    test_files = {
        "background.mp4": "background video",
        "post.png": "screenshot image",
        "subtitles.srt": "subtitle file",
        "audio.mp3": "audio file"
    }
    
    all_exist = all(os.path.exists(f) for f in test_files.keys())
    
    if all_exist:
        print("\n✅ All test files found! Running composition...")
        result = compose_video_with_ffmpeg(
            background_video="background.mp4",
            screenshot_image="post.png",
            subtitle_file="subtitles.srt",
            audio_file="audio.mp3",
            output_file="test_output.mp4"
        )
        if result:
            print(f"\n✅ Test successful! Output: {result}")
    else:
        print("\n⚠️  Missing test files:")
        for file, desc in test_files.items():
            status = "✅" if os.path.exists(file) else "❌"
            print(f"   {status} {file} ({desc})")
