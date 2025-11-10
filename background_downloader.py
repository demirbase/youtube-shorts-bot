# background_downloader.py
# Downloads background videos using yt-dlp

import yt_dlp
import os

def download_background_video(
    query: str = "minecraft parkour gameplay no commentary", 
    output_file: str = "background.mp4",
    max_duration: int = 120
) -> str | None:
    """
    Downloads the first search result from YouTube for a given query.
    
    Args:
        query: Search query for YouTube
        output_file: Path to save the downloaded video
        max_duration: Maximum video duration in seconds (default 120)
        
    Returns:
        Path to downloaded video, or None on failure
    """
    print(f"🔍 Searching for background video: '{query}'")
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'best[height<=1080][ext=mp4]',  # 1080p max, MP4 format
        'outtmpl': output_file,
        'default_search': 'ytsearch1',  # Search YouTube and get first result
        'match_filter': f'duration < {max_duration}',  # Filter by duration
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the first video found
            ydl.download([query])
        
        if os.path.exists(output_file):
            print(f"✅ Background video downloaded: {output_file}")
            return output_file
        else:
            print(f"❌ Failed to download video (file not created)")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading background video: {e}")
        return None


def get_random_background_query() -> str:
    """
    Returns a random background video query for variety.
    """
    import random
    
    queries = [
        "minecraft parkour gameplay no commentary",
        "subway surfers gameplay no commentary",
        "satisfying gameplay no commentary",
        "relaxing minecraft gameplay",
        "mobile game gameplay no commentary"
    ]
    
    return random.choice(queries)
