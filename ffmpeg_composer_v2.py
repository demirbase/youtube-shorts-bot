#!/usr/bin/env python3
"""
ffmpeg_composer_v2.py
Gelişmiş 4 katmanlı video montajı:
1. Arka plan videosu (Pexels - dinamik)
2. Reddit çerçevesi (PIL - şeffaf metin alanı)
3. Altyazılar (edge-tts - yakılmış)
4. Ses (edge-tts - senkronize)
"""

import subprocess
import os
import json


def get_video_duration(video_path: str) -> float | None:
    """
    Videonun süresini ffprobe ile alır.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        
        return duration
        
    except Exception as e:
        print(f"⚠️  Could not get video duration: {e}")
        return None


def compose_video_v2(
    background_video: str,
    reddit_frame: str,
    subtitle_file: str,
    audio_file: str,
    output_file: str = "final_short.mp4",
    target_width: int = 1080,
    target_height: int = 1920,
    subtitle_style: dict = None
) -> str | None:
    """
    4 katmanlı gelişmiş video montajı yapar.
    
    Katmanlar:
    1. Arka plan videosu (scale + crop to 9:16)
    2. Reddit çerçevesi (overlay)
    3. Altyazılar (burned subtitles)
    4. Ses (audio track)
    
    Args:
        background_video: Arka plan videosu (Pexels'tan)
        reddit_frame: Reddit çerçevesi PNG (şeffaf alan)
        subtitle_file: SRT altyazı dosyası
        audio_file: Ses dosyası
        output_file: Çıktı dosyası
        target_width: Hedef genişlik (1080)
        target_height: Hedef yükseklik (1920)
        subtitle_style: Altyazı stil ayarları
        
    Returns:
        Oluşturulan dosya yolu veya None
    """
    print("🎬 Composing video with 4-layer architecture...")
    print(f"   Background: {background_video}")
    print(f"   Frame: {reddit_frame}")
    print(f"   Subtitles: {subtitle_file}")
    print(f"   Audio: {audio_file}")
    
    # Dosyaları kontrol et
    required_files = [background_video, reddit_frame, subtitle_file, audio_file]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            return None
    
    # Altyazı stil ayarları
    if subtitle_style is None:
        subtitle_style = {
            'font': 'Arial',
            'font_size': 32,
            'primary_color': '&H00FFFFFF',  # Beyaz
            'outline_color': '&H00000000',  # Siyah çerçeve
            'outline': 2,
            'shadow': 2,
            'bold': 1,
            'alignment': 2,  # Alt orta
            'margin_v': 180  # Alttan boşluk
        }
    
    # Altyazı dosyasını escape et (Windows path için)
    sub_path = subtitle_file.replace('\\', '/').replace(':', '\\:')
    
    # FFmpeg filter_complex zinciri
    # [0:v] = background video
    # [1:v] = reddit frame (PNG with alpha)
    
    filter_complex = (
        # KATMAN 1: Arka plan videosu - 9:16'ya ölçekle ve kırp
        f"[0:v]scale=w={target_width}:h={target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height}[bg];"
        
        # KATMAN 2: Reddit çerçevesini üst üste bindirme
        f"[1:v]scale={target_width}:-1[frame];"
        f"[bg][frame]overlay=x=0:y=(main_h-overlay_h)/2:format=auto[video_with_frame];"
        
        # KATMAN 3: Altyazıları yakma
        f"[video_with_frame]subtitles='{sub_path}':force_style='"
        f"FontName={subtitle_style['font']},"
        f"FontSize={subtitle_style['font_size']},"
        f"PrimaryColour={subtitle_style['primary_color']},"
        f"OutlineColour={subtitle_style['outline_color']},"
        f"Outline={subtitle_style['outline']},"
        f"Shadow={subtitle_style['shadow']},"
        f"Bold={subtitle_style['bold']},"
        f"Alignment={subtitle_style['alignment']},"
        f"MarginV={subtitle_style['margin_v']}"
        f"'[final_v]"
    )
    
    # FFmpeg komutu
    cmd = [
        "ffmpeg",
        "-i", background_video,  # Input 0: arka plan
        "-i", reddit_frame,      # Input 1: çerçeve
        "-i", audio_file,        # Input 2: ses
        "-filter_complex", filter_complex,
        "-map", "[final_v]",     # Video output
        "-map", "2:a",           # Audio output (input 2)
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",             # Ses süresiyle eşleştir
        "-movflags", "+faststart",
        "-y",
        output_file
    ]
    
    print()
    print("⚙️  FFmpeg filter_complex:")
    print("   1. Scale background to 9:16")
    print("   2. Overlay Reddit frame")
    print("   3. Burn subtitles (karaoke style)")
    print("   4. Sync with audio")
    print()
    print("⏳ Processing video (this may take 30-60 seconds)...")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Başarılı
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            duration = get_video_duration(output_file)
            
            print(f"✅ Video composed successfully: {output_file}")
            print(f"   Size: {file_size:.1f} MB")
            if duration:
                print(f"   Duration: {duration:.1f}s")
            
            return output_file
        else:
            print("❌ Output file not created")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error:")
        print(f"   Return code: {e.returncode}")
        if e.stderr:
            # Son 10 satırı göster
            error_lines = e.stderr.split('\n')
            print("   Last error lines:")
            for line in error_lines[-10:]:
                if line.strip():
                    print(f"     {line}")
        return None
        
    except Exception as e:
        print(f"❌ Error composing video: {e}")
        return None


def test_compose_simple(
    background_video: str,
    audio_file: str,
    text_overlay: str = "Test Text",
    output_file: str = "test_output.mp4"
) -> str | None:
    """
    Basit test için: Arka plan + ses + metin overlay
    """
    print("🧪 Simple composition test...")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", background_video,
            "-i", audio_file,
            "-filter_complex",
            (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920[v];"
                f"[v]drawtext=text='{text_overlay}':fontsize=40:fontcolor=white:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5[final_v]"
            ),
            "-map", "[final_v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            "-y",
            output_file
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        if os.path.exists(output_file):
            print(f"✅ Test video created: {output_file}")
            return output_file
        
        return None
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


if __name__ == "__main__":
    print("🧪 Testing FFmpeg composer v2...")
    print("=" * 60)
    print()
    print("This module requires:")
    print("  1. background.mp4 (from pexels_dynamic.py)")
    print("  2. reddit_frame.png (from reddit_frame_creator.py)")
    print("  3. subtitles.srt (from subtitle_generator_v2.py)")
    print("  4. narration.mp3 (from subtitle_generator_v2.py)")
    print()
    print("Run the full pipeline with main_v4.py")
