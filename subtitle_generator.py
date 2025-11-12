# subtitle_generator.py
# Generates audio with edge-tts AND creates synchronized .srt subtitle files

import asyncio
import edge_tts
import os
import re
from datetime import timedelta


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format: 00:00:00,000
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


async def generate_audio_with_subtitles(
    text: str,
    audio_file: str = "output.mp3",
    subtitle_file: str = "output.srt",
    voice: str = "en-US-GuyNeural",
    rate: str = "+30%"
) -> tuple[str, str] | None:
    """
    Generate audio using edge-tts AND create .srt subtitle file.
    
    Args:
        text: Text to convert to speech
        audio_file: Output audio file path
        subtitle_file: Output subtitle file path
        voice: edge-tts voice name
        rate: Speed adjustment (+30% = 1.3x speed, like Turkish spec)
        
    Returns:
        Tuple of (audio_path, subtitle_path) or None on failure
    """
    print(f"🎤 Generating audio with edge-tts...")
    print(f"   Voice: {voice}")
    print(f"   Speed: {rate}")
    
    try:
        # Create edge-tts Communicate object
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        # Collect subtitles data
        subtitles = []
        current_time = 0.0
        
        # Save audio and collect subtitle info
        with open(audio_file, "wb") as audio_fp:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_fp.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # WordBoundary contains timing info
                    offset = chunk["offset"] / 10_000_000  # Convert from 100ns to seconds
                    duration = chunk["duration"] / 10_000_000
                    word = chunk["text"]
                    
                    subtitles.append({
                        "start": offset,
                        "end": offset + duration,
                        "text": word
                    })
        
        print(f"✅ Audio saved: {audio_file}")
        
        # Generate .srt file from subtitle data
        if subtitles:
            # Group words into subtitle chunks (every 3-5 words)
            chunk_size = 4
            subtitle_chunks = []
            
            for i in range(0, len(subtitles), chunk_size):
                chunk = subtitles[i:i + chunk_size]
                text_combined = " ".join([s["text"] for s in chunk])
                start_time = chunk[0]["start"]
                end_time = chunk[-1]["end"]
                
                subtitle_chunks.append({
                    "start": start_time,
                    "end": end_time,
                    "text": text_combined
                })
            
            # Write .srt file
            with open(subtitle_file, "w", encoding="utf-8") as srt_fp:
                for idx, chunk in enumerate(subtitle_chunks, start=1):
                    srt_fp.write(f"{idx}\n")
                    srt_fp.write(f"{format_timestamp(chunk['start'])} --> {format_timestamp(chunk['end'])}\n")
                    srt_fp.write(f"{chunk['text']}\n")
                    srt_fp.write("\n")
            
            print(f"✅ Subtitles saved: {subtitle_file}")
            print(f"   Generated {len(subtitle_chunks)} subtitle entries")
            return (audio_file, subtitle_file)
        else:
            print("⚠️  No subtitle data received from edge-tts")
            return (audio_file, None)
            
    except Exception as e:
        print(f"❌ Error generating audio/subtitles: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_audio_with_subtitles_sync(
    text: str,
    audio_file: str = "output.mp3",
    subtitle_file: str = "output.srt",
    voice: str = "en-US-GuyNeural",
    rate: str = "+30%"
) -> tuple[str, str] | None:
    """
    Synchronous wrapper for generate_audio_with_subtitles.
    Use this in non-async code.
    """
    return asyncio.run(generate_audio_with_subtitles(
        text, audio_file, subtitle_file, voice, rate
    ))


# Voice presets for different languages/styles
VOICE_PRESETS = {
    "male_en": "en-US-GuyNeural",
    "female_en": "en-US-AriaNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_au": "en-AU-WilliamNeural",
    "female_au": "en-AU-NatashaNeural",
    "male_deep": "en-US-EricNeural",  # Deeper voice
    "female_young": "en-US-JennyNeural",  # Younger sounding
}


if __name__ == "__main__":
    # Test with sample text
    test_text = """
    This is a test of the edge-tts subtitle generation system.
    It should create both audio and synchronized subtitles.
    The subtitles will be burned into the final video using FFmpeg.
    """
    
    print("Testing edge-tts with subtitle generation...")
    result = generate_audio_with_subtitles_sync(
        test_text.strip(),
        audio_file="test_audio.mp3",
        subtitle_file="test_subtitles.srt",
        voice=VOICE_PRESETS["male_en"],
        rate="+30%"
    )
    
    if result:
        audio_path, subtitle_path = result
        print(f"\n✅ Test successful!")
        print(f"   Audio: {audio_path}")
        print(f"   Subtitles: {subtitle_path}")
        
        # Show a sample of the .srt file
        if subtitle_path and os.path.exists(subtitle_path):
            print("\n📄 First few subtitle entries:")
            with open(subtitle_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:20]  # First 20 lines
                print("".join(lines))
    else:
        print("\n❌ Test failed.")
