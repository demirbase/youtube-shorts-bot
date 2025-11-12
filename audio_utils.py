# audio_utils.py
# Audio processing utilities for V2 enhancements
# Fixed: Removed conflicting subprocess arguments

import subprocess
import os

def speed_up_audio(input_wav: str, output_wav: str, speed: float = 1.3) -> str | None:
    """
    Speeds up an audio file using FFmpeg's atempo filter.
    A speed of 1.3 means 1.3x faster.
    
    The atempo filter is limited to values between 0.5 and 2.0.
    For speeds > 2.0, chain multiple atempo filters.
    
    Args:
        input_wav: Path to input audio file
        output_wav: Path to output audio file
        speed: Speed multiplier (1.3 = 30% faster, 1.5 = 50% faster)
        
    Returns:
        Path to output file, or None on failure
    """
    print(f"⚡ Speeding up audio to {speed}x...")
    
    # Validate speed
    if speed < 0.5 or speed > 4.0:
        print(f"⚠️  Speed {speed} out of safe range (0.5-4.0). Using 1.3x")
        speed = 1.3
    
    try:
        # If speed > 2.0, we need to chain atempo filters
        if speed > 2.0:
            # Split into multiple stages
            # e.g., 3x = 1.5x * 2x
            filter_chain = f"atempo={speed/2},atempo=2.0"
        else:
            filter_chain = f"atempo={speed}"
        
        command = [
            "ffmpeg",
            "-i", input_wav,
            "-filter:a", filter_chain,
            "-vn",  # No video
            "-y",  # Overwrite output
            output_wav
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        print(f"✅ Successfully sped up audio: {output_wav}")
        return output_wav
        
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No error details"
        print(f"❌ Error speeding up audio: {stderr_output}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_audio_duration(file_path: str) -> float:
    """Gets the duration of an audio file using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting audio duration: {e}. Defaulting to 60 seconds.")
        return 60.0
