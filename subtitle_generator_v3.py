#!/usr/bin/env python3
"""
subtitle_generator_v3.py
Fallback audio generator using gTTS (Google Text-to-Speech)
More reliable than edge-tts for production use
"""

from gtts import gTTS
import os
from datetime import timedelta


def format_srt_time(seconds: float) -> str:
    """
    Converts seconds to SRT time format: 00:00:10,500
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def estimate_speech_duration(text: str, wpm: int = 150) -> float:
    """
    Estimates speech duration based on word count.
    
    Args:
        text: Text to estimate
        wpm: Words per minute (default 150 for normal speech)
        
    Returns:
        Duration in seconds
    """
    words = len(text.split())
    duration = (words / wpm) * 60
    return duration


def generate_audio_with_flow_gtts(
    title: str,
    comments: list[dict],
    audio_file: str = "narration.mp3",
    subtitle_file: str = "subtitles.srt",
    lang: str = "en",
    slow: bool = False,
    pause_between: float = 1.0
) -> tuple[str, str] | None:
    """
    Generates audio and subtitles with question > answer flow using gTTS.
    
    Args:
        title: Post title (question)
        comments: List of comments [{'author': 'user1', 'body': 'text'}, ...]
        audio_file: Audio output file
        subtitle_file: Subtitle output file
        lang: Language code (en, tr, etc.)
        slow: Whether to use slow speech
        pause_between: Pause between question/answers (seconds)
        
    Returns:
        (audio_file, subtitle_file) or None
    """
    print("🎤 Generating audio with gTTS (Google Text-to-Speech)...")
    print(f"   Language: {lang}")
    print(f"   Title + {len(comments)} comments")
    
    try:
        # Prepare segments
        segments = []
        
        # Segment 1: Question
        segments.append({
            'type': 'question',
            'text': f"The question is: {title}"
        })
        
        # Segments 2-N: Answers
        for i, comment in enumerate(comments, 1):
            segments.append({
                'type': 'answer',
                'text': f"Answer {i}: {comment['body']}"
            })
        
        print(f"   Prepared {len(segments)} segments")
        
        # Generate audio segments and combine
        temp_files = []
        current_time = 0.0
        subtitle_entries = []
        subtitle_index = 1
        
        for seg_idx, segment in enumerate(segments):
            # Generate audio for this segment
            temp_file = f"temp_segment_{seg_idx}.mp3"
            temp_files.append(temp_file)
            
            tts = gTTS(text=segment['text'], lang=lang, slow=slow)
            tts.save(temp_file)
            
            # Estimate duration
            duration = estimate_speech_duration(segment['text'])
            
            # Create subtitle entry
            start_time = current_time
            end_time = current_time + duration
            
            subtitle_entries.append({
                'index': subtitle_index,
                'start': start_time,
                'end': end_time,
                'text': segment['text']
            })
            
            subtitle_index += 1
            current_time = end_time + pause_between
        
        # Combine audio files using ffmpeg
        print("   Combining audio segments...")
        
        # Create concat file for ffmpeg
        concat_file = "temp_concat.txt"
        with open(concat_file, 'w') as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
                # Add silence between segments
                if temp_file != temp_files[-1]:
                    f.write(f"file 'silence.mp3'\n")
        
        # Generate silence file if needed
        import subprocess
        silence_duration = pause_between
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 
            f'anullsrc=r=44100:cl=mono:d={silence_duration}',
            '-y', 'silence.mp3'
        ], check=True, capture_output=True)
        
        # Combine all segments
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y', audio_file
        ], check=True, capture_output=True)
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(concat_file):
            os.remove(concat_file)
        if os.path.exists('silence.mp3'):
            os.remove('silence.mp3')
        
        # Write subtitle file
        print("   Writing subtitle file...")
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            for entry in subtitle_entries:
                f.write(f"{entry['index']}\n")
                f.write(f"{format_srt_time(entry['start'])} --> {format_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n")
                f.write("\n")
        
        print(f"✅ Audio saved: {audio_file}")
        print(f"✅ Subtitles saved: {subtitle_file}")
        print(f"   Total duration: ~{current_time:.1f}s")
        
        return (audio_file, subtitle_file)
        
    except Exception as e:
        print(f"❌ Error generating audio/subtitles: {e}")
        return None


if __name__ == "__main__":
    # Test
    print("🧪 Testing gTTS audio generator...")
    
    test_title = "What's the most interesting fact you know?"
    test_comments = [
        {'author': 'user1', 'body': 'Honey never spoils. Archaeologists found 3000-year-old honey that was still edible.'},
        {'author': 'user2', 'body': 'There are more possible chess games than atoms in the universe.'}
    ]
    
    result = generate_audio_with_flow_gtts(
        title=test_title,
        comments=test_comments,
        audio_file="test_gtts_audio.mp3",
        subtitle_file="test_gtts_subs.srt"
    )
    
    if result:
        print("\n✅ Test successful!")
    else:
        print("\n❌ Test failed!")
