#!/usr/bin/env python3
"""
pexels_dynamic.py
Her seferinde farklı arka plan videosu indirir (Pexels API)
Çeşitlilik için 20+ farklı arama terimi
"""

import requests
import random
import os


# 20+ farklı arka plan kategorisi (dinamik içerik için)
BACKGROUND_QUERIES = [
    # Oyun teması
    "minecraft parkour gameplay",
    "subway surfers gameplay",
    "temple run gameplay",
    "mobile game satisfying",
    
    # Rahatlatıcı/ASMR
    "satisfying slime asmr",
    "kinetic sand cutting",
    "soap cutting asmr",
    "oddly satisfying video",
    
    # Doğa
    "ocean waves relaxing",
    "rain forest nature",
    "northern lights aurora",
    "underwater coral reef",
    
    # Soyut/Hipnotik
    "abstract moving patterns",
    "hypnotic spiral animation",
    "colorful fluid motion",
    "geometric patterns moving",
    
    # Spor/Hareket
    "parkour free running",
    "skateboard tricks slow motion",
    "basketball trick shots",
    "extreme sports aerial"
]


def get_random_background_video(
    output_file: str = "background.mp4",
    api_key: str = None,
    min_duration: int = 30,
    max_duration: int = 90
) -> str | None:
    """
    Pexels'tan rastgele bir arka plan videosu indirir.
    
    Args:
        output_file: Çıktı dosyası
        api_key: Pexels API key (yoksa env'den alır)
        min_duration: Minimum süre (saniye)
        max_duration: Maximum süre (saniye)
        
    Returns:
        İndirilen dosya yolu veya None
    """
    
    # API key al
    if not api_key:
        api_key = os.environ.get('PEXELS_API_KEY')
    
    if not api_key:
        print("❌ PEXELS_API_KEY not found in environment")
        print("   Get free key: https://www.pexels.com/api/")
        return None
    
    # Rastgele sorgu seç
    query = random.choice(BACKGROUND_QUERIES)
    print(f"🎬 Searching Pexels for: '{query}'")
    
    # Pexels Video API
    search_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    
    params = {
        "query": query,
        "orientation": "portrait",  # 9:16 için
        "size": "medium",
        "per_page": 15  # Daha fazla seçenek
    }
    
    try:
        print("   Fetching videos from Pexels API...")
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        videos = data.get('videos', [])
        
        if not videos:
            print(f"❌ No videos found for query: {query}")
            return None
        
        print(f"✅ Found {len(videos)} videos")
        
        # Süre filtreleme
        suitable_videos = []
        for video in videos:
            duration = video.get('duration', 0)
            if min_duration <= duration <= max_duration:
                suitable_videos.append(video)
        
        if not suitable_videos:
            print("   No videos in duration range, using best match...")
            suitable_videos = videos[:5]  # İlk 5'i kullan
        
        # Rastgele bir video seç
        selected_video = random.choice(suitable_videos)
        duration = selected_video.get('duration', 0)
        
        print(f"   Selected video duration: {duration}s")
        
        # En iyi kaliteli video dosyasını bul
        video_files = selected_video.get('video_files', [])
        
        # Portrait ve HD kalite tercih et
        best_file = None
        for vf in video_files:
            if vf.get('width', 0) == 1080 or vf.get('height', 0) == 1920:
                best_file = vf
                break
        
        # Bulamazsa en yüksek kaliteyi al
        if not best_file and video_files:
            best_file = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
        
        if not best_file:
            print("❌ No suitable video file found")
            return None
        
        download_url = best_file.get('link')
        file_size_mb = best_file.get('file_size', 0) / (1024 * 1024)
        
        print(f"   Downloading video ({file_size_mb:.1f} MB)...")
        
        # Videoyu indir
        video_response = requests.get(download_url, stream=True, timeout=30)
        video_response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        actual_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✅ Background video downloaded: {output_file}")
        print(f"   Query: {query}")
        print(f"   Duration: {duration}s")
        print(f"   Size: {actual_size:.1f} MB")
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None


def get_background_for_duration(
    target_duration: float,
    output_file: str = "background.mp4",
    api_key: str = None
) -> str | None:
    """
    Belirli bir sürece uygun arka plan videosu indirir.
    
    Args:
        target_duration: Hedef süre (saniye)
        output_file: Çıktı dosyası
        api_key: Pexels API key
        
    Returns:
        İndirilen dosya yolu veya None
    """
    # Hedef süreye göre aralık belirle (+/-20 saniye tolerans)
    min_dur = max(30, int(target_duration - 20))
    max_dur = int(target_duration + 20)
    
    print(f"📐 Looking for background video: {min_dur}s - {max_dur}s")
    
    return get_random_background_video(
        output_file=output_file,
        api_key=api_key,
        min_duration=min_dur,
        max_duration=max_dur
    )


if __name__ == "__main__":
    # Test
    print("🧪 Testing dynamic background downloader...")
    print("=" * 60)
    print()
    
    result = get_random_background_video(output_file="test_background.mp4")
    
    if result:
        print()
        print("✅ Test successful!")
        print(f"   Video downloaded: {result}")
        print()
        print("🔄 Each time this runs, you get a DIFFERENT video!")
        print(f"   {len(BACKGROUND_QUERIES)} different categories available")
    else:
        print()
        print("❌ Test failed")
        print("   Make sure PEXELS_API_KEY is set in environment")
