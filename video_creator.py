# video_creator.py
# Generates audio with edge-tts and assembles the video with FFmpeg.

import subprocess
import asyncio
import edge_tts
import re

# Configuration for the TTS
VOICE = "en-US-JennyNeural"  # A high-quality, natural-sounding voice
OUTPUT_AUDIO_FILE = "output.mp3"
OUTPUT_SRT_FILE = "output.srt"
OUTPUT_VIDEO_FILE = "output.mp4"
BACKGROUND_IMAGE = "background.png"  # Must exist in the repo

def generate_srt(text: str, audio_duration: float, max_words_per_line=5) -> str:
    """
    Generates a simple .srt subtitle file from the text.
    
    Args:
        text: The full text to be subtitled.
        audio_duration: The total duration of the audio in seconds.
        max_words_per_line: Max words per subtitle line.
    """
    print("Generating subtitles...")
    words = re.findall(r"[\w']+|[.,!?;]", text)
    total_words = len(words)
    if total_words == 0:
        return ""

    duration_per_word = audio_duration / total_words
    
    srt_content = ""
    start_time = 0.0
    subtitle_index = 1

    for i in range(0, total_words, max_words_per_line):
        chunk = words[i:i + max_words_per_line]
        if not chunk:
            continue
            
        end_time = start_time + (len(chunk) * duration_per_word)
        
        # Format start time: HH:MM:SS,ms
        start_h, start_rem = divmod(start_time, 3600)
        start_m, start_s = divmod(start_rem, 60)
        start_ms = int((start_s - int(start_s)) * 1000)
        start_time_str = f"{int(start_h):02}:{int(start_m):02}:{int(start_s):02},{start_ms:03}"
        
        # Format end time
        end_h, end_rem = divmod(end_time, 3600)
        end_m, end_s = divmod(end_rem, 60)
        end_ms = int((end_s - int(end_s)) * 1000)
        end_time_str = f"{int(end_h):02}:{int(end_m):02}:{int(end_s):02},{end_ms:03}"

        # Add to SRT content
        srt_content += f"{subtitle_index}\n"
        srt_content += f"{start_time_str} --> {end_time_str}\n"
        srt_content += " ".join(chunk) + "\n\n"
        
        start_time = end_time
        subtitle_index += 1

    with open(OUTPUT_SRT_FILE, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    print(f"Subtitles saved to {OUTPUT_SRT_FILE}")
    return OUTPUT_SRT_FILE

async def _generate_audio(text: str, file_path: str):
    """Async helper to generate and save audio using edge-tts."""
    print("Generating audio with edge-tts...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file_path)
    print(f"Audio saved to {file_path}")

def get_audio_duration(file_path: str) -> float:
    """Gets the duration of an audio file using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting audio duration: {e}. Defaulting to 60 seconds.")
        return 60.0

def create_video_from_post(post_data: dict) -> str | None:
    """
    Orchestrates the creation of the video file.
    
    Args:
        post_data: The dictionary from reddit_scraper.

    Returns:
        The path to the final video file, or None on failure.
    """
    try:
        full_text = f"{post_data['title']}. {post_data['body']}"
        
        # 1. Generate Audio
        asyncio.run(_generate_audio(full_text, OUTPUT_AUDIO_FILE))
        
        # 2. Get Audio Duration
        audio_duration = get_audio_duration(OUTPUT_AUDIO_FILE)
        
        # 3. Generate Subtitles
        generate_srt(full_text, audio_duration)

        # 4. Assemble Video with FFmpeg
        print("Assembling video with FFmpeg...")
        
        # This complex FFmpeg command does the following:
        # -loop 1 -i {image}: Loops the static background image
        # -i {audio}: Adds the generated MP3 audio
        # -vf "scale=...": Resizes the image to fit 1080x1920 (9:16 aspect ratio).
        #     - force_original_aspect_ratio=decrease: Fits image within 1080x1920
        #     - pad=1080:1920:(ow-iw)/2:(oh-ih)/2: Adds black bars to fill 1080x1920
        #     - subtitles=...: Burns the subtitles onto the video with styling
        # -c:v libx264 -tune stillimage: Optimizes video encoding for a static image
        # -c:a aac -b:a 192k: Encodes audio to AAC format
        # -pix_fmt yuv420p: Ensures compatibility with most players
        # -shortest: Truncates the video to match the (shorter) audio duration
        
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-loop', '1',
            '-i', BACKGROUND_IMAGE,
            '-i', OUTPUT_AUDIO_FILE,
            '-vf', (
                f"scale=1080:1920:force_original_aspect_ratio=decrease,"
                f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
                f"subtitles={OUTPUT_SRT_FILE}:force_style='"
                f"FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,"
                f"OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,"
                f"MarginV=50,Alignment=10'"
            ),
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            OUTPUT_VIDEO_FILE
        ]

        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        
        print(f"Video successfully created: {OUTPUT_VIDEO_FILE}")
        return OUTPUT_VIDEO_FILE

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Video creation failed: {e}")
        return None
