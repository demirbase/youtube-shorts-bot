#!/usr/bin/env python3
"""
subtitle_generator_v2.py
Gelişmiş altyazı üreteci: Soru > Cevap akışı
Cümle düzeyinde karaoke efekti (edge-tts ile)
"""

import edge_tts
import asyncio
import re
from datetime import timedelta


def format_srt_time(seconds: float) -> str:
    """
    Saniyeyi SRT zaman formatına çevirir: 00:00:10,500
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


async def generate_audio_with_flow(
    title: str,
    comments: list[dict],
    audio_file: str = "narration.mp3",
    subtitle_file: str = "subtitles.srt",
    voice: str = "en-US-GuyNeural",
    rate: str = "+10%",
    pause_between: float = 0.5  # Soru-cevap arası duraklama
) -> tuple[str, str] | None:
    """
    Soru > Cevap akışı ile ses ve altyazı üretir.
    
    Args:
        title: Post başlığı (soru)
        comments: Yorumlar listesi [{'author': 'user1', 'body': 'text'}, ...]
        audio_file: Ses çıktısı
        subtitle_file: Altyazı çıktısı
        voice: edge-tts sesi
        rate: Konuşma hızı (+10% = 1.1x)
        pause_between: Soru-cevap arası duraklama (saniye)
        
    Returns:
        (audio_file, subtitle_file) veya None
    """
    print("🎤 Generating audio with question > answer flow...")
    print(f"   Voice: {voice}")
    print(f"   Rate: {rate}")
    print(f"   Title + {len(comments)} comments")
    
    try:
        # Metni hazırla: Başlık + Yorumlar
        segments = []
        
        # SEGMENT 1: Başlık (Soru)
        segments.append({
            'text': title,
            'type': 'question',
            'speaker': 'narrator'
        })
        
        # SEGMENT 2-N: Yorumlar (Cevaplar)
        for i, comment in enumerate(comments[:5], 1):  # İlk 5 yorum
            author = comment.get('author', f'user{i}')
            body = comment.get('body', '')
            
            # Uzun yorumları kısalt
            if len(body) > 200:
                body = body[:197] + "..."
            
            segments.append({
                'text': body,
                'type': 'answer',
                'speaker': author
            })
        
        print(f"   Prepared {len(segments)} segments (1 question + {len(segments)-1} answers)")
        
        # Tam metni oluştur (duraklama işaretleriyle)
        full_text = ""
        for i, seg in enumerate(segments):
            full_text += seg['text']
            # Soru-cevap arası veya cevaplar arası duraklama
            if i < len(segments) - 1:
                # edge-tts için duraklama: <break time="500ms"/>
                pause_ms = int(pause_between * 1000)
                full_text += f' <break time="{pause_ms}ms"/> '
        
        print(f"   Total text length: {len(full_text)} characters")
        
        # edge-tts ile ses ve zamanlama üret
        communicate = edge_tts.Communicate(full_text, voice, rate=rate)
        
        submaker = edge_tts.SubMaker()
        
        # Ses üret ve zamanlama bilgisini topla
        print("   Generating audio with edge-tts...")
        with open(audio_file, "wb") as audio_out:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_out.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Kelime zamanlama bilgisi
                    submaker.create_sub(
                        (chunk["offset"], chunk["duration"]),
                        chunk["text"]
                    )
        
        print(f"✅ Audio generated: {audio_file}")
        
        # Altyazı dosyası oluştur
        print("   Generating subtitles...")
        
        # edge-tts'in ürettiği altyazıları al
        raw_subs = submaker.generate_subs()
        
        # Altyazıları grupla (4-5 kelime chunks)
        grouped_subs = group_subtitles(raw_subs, words_per_chunk=4)
        
        # SRT formatında kaydet
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(grouped_subs, 1):
                f.write(f"{i}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n\n")
        
        print(f"✅ Subtitles generated: {subtitle_file}")
        print(f"   Total subtitle chunks: {len(grouped_subs)}")
        
        # Segment sınırlarını göster (debug)
        print()
        print("📋 Flow structure:")
        cumulative_chars = 0
        for i, seg in enumerate(segments, 1):
            seg_len = len(seg['text'])
            cumulative_chars += seg_len
            print(f"   {i}. [{seg['type'].upper():8s}] {seg_len:3d} chars - \"{seg['text'][:50]}...\"")
        
        return (audio_file, subtitle_file)
        
    except Exception as e:
        print(f"❌ Error generating audio/subtitles: {e}")
        import traceback
        traceback.print_exc()
        return None


def group_subtitles(raw_subs: str, words_per_chunk: int = 4) -> list[dict]:
    """
    Ham altyazıları gruplar (karaoke efekti için).
    
    Args:
        raw_subs: edge-tts'den gelen SRT formatı
        words_per_chunk: Chunk başına kelime sayısı
        
    Returns:
        [{'start': '00:00:01,000', 'end': '00:00:02,500', 'text': 'word1 word2'}, ...]
    """
    lines = raw_subs.strip().split('\n')
    
    # SRT parse et
    subs = []
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            idx = int(lines[i].strip())
            i += 1
            if i < len(lines):
                timing = lines[i].strip()
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                
                if '-->' in timing:
                    start, end = timing.split('-->')
                    subs.append({
                        'start': start.strip(),
                        'end': end.strip(),
                        'text': ' '.join(text_lines)
                    })
        i += 1
    
    # Kelimeleri grupla
    grouped = []
    current_group = []
    current_start = None
    current_end = None
    
    for sub in subs:
        words = sub['text'].split()
        
        if not current_start:
            current_start = sub['start']
        
        current_group.extend(words)
        current_end = sub['end']
        
        # Grup dolduğunda kaydet
        if len(current_group) >= words_per_chunk:
            grouped.append({
                'start': current_start,
                'end': current_end,
                'text': ' '.join(current_group)
            })
            current_group = []
            current_start = None
            current_end = None
    
    # Kalan kelimeleri ekle
    if current_group and current_start:
        grouped.append({
            'start': current_start,
            'end': current_end,
            'text': ' '.join(current_group)
        })
    
    return grouped


def generate_audio_with_flow_sync(
    title: str,
    comments: list[dict],
    **kwargs
) -> tuple[str, str] | None:
    """
    Senkron wrapper (main script için).
    """
    return asyncio.run(generate_audio_with_flow(title, comments, **kwargs))


# Ses presets (voice options)
VOICE_PRESETS_V2 = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-AriaNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_deep": "en-US-EricNeural",
    "female_young": "en-US-JennyNeural",
}


if __name__ == "__main__":
    # Test
    print("🧪 Testing flow-based subtitle generator...")
    print("=" * 60)
    print()
    
    test_title = "What's something that everyone should experience at least once in their lifetime?"
    test_comments = [
        {'author': 'user1', 'body': 'Traveling to a foreign country where you don\'t speak the language. It really opens your mind.'},
        {'author': 'user2', 'body': 'Working in customer service. You learn patience and empathy like nowhere else.'},
        {'author': 'user3', 'body': 'Living alone for at least a year. You discover so much about yourself.'},
    ]
    
    result = generate_audio_with_flow_sync(
        title=test_title,
        comments=test_comments,
        audio_file="test_narration.mp3",
        subtitle_file="test_subtitles.srt"
    )
    
    if result:
        audio, subs = result
        print()
        print("✅ Test successful!")
        print(f"   Audio: {audio}")
        print(f"   Subtitles: {subs}")
        print()
        print("🎬 This creates:")
        print("   • Question first, then answers")
        print("   • Pauses between segments")
        print("   • Sentence-level karaoke timing")
    else:
        print()
        print("❌ Test failed")
