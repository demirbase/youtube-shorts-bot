# pexels_downloader.py
# Downloads background videos from Pexels API (free, no credit card required)

import requests
import os

# Get your free API key from: https://www.pexels.com/api/
# Add it as PEXELS_API_KEY environment variable or GitHub secret

def download_pexels_video(
    query: str = "abstract moving background",
    output_file: str = "background.mp4",
    api_key: str = None,
    orientation: str = "portrait",  # For 9:16 Shorts
    size: str = "medium"
) -> str | None:
    """
    Downloads a video from Pexels API for use as background.
    
    Pexels API is 100% free with generous limits:
    - 200 requests per hour
    - 20,000 requests per month
    - No credit card required
    
    Args:
        query: Search term (e.g., "parkour", "abstract", "relaxing")
        output_file: Path to save downloaded video
        api_key: Pexels API key (from env var if not provided)
        orientation: "portrait" for 9:16, "landscape", or "square"
        size: "small", "medium", "large" (affects file size)
        
    Returns:
        Path to downloaded video, or None on failure
    """
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get('PEXELS_API_KEY')
    
    if not api_key:
        print("❌ PEXELS_API_KEY not found in environment variables")
        print("   Get your free API key from: https://www.pexels.com/api/")
        print("   Then add it as an environment variable or GitHub secret")
        return None
    
    print(f"🎬 Searching Pexels for '{query}' videos...")
    
    # Pexels Video API endpoint
    search_url = "https://api.pexels.com/videos/search"
    
    headers = {
        "Authorization": api_key
    }
    
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": 15,  # Get 15 results to choose from
        "page": 1
    }
    
    try:
        # Search for videos
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        videos = data.get('videos', [])
        
        if not videos:
            print(f"⚠️  No videos found for query: '{query}'")
            return None
        
        # Pick the first video (you can randomize this)
        video = videos[0]
        video_files = video.get('video_files', [])
        
        # Find the video file with desired quality
        # Filter by dimensions suitable for 9:16 (portrait)
        suitable_file = None
        for vf in video_files:
            if vf.get('quality') == size and vf.get('width', 0) >= 720:
                suitable_file = vf
                break
        
        # Fallback to any HD file
        if not suitable_file:
            for vf in video_files:
                if vf.get('width', 0) >= 720:
                    suitable_file = vf
                    break
        
        if not suitable_file and video_files:
            # Last resort: use first available file
            suitable_file = video_files[0]
        
        if not suitable_file:
            print("⚠️  No suitable video file found")
            return None
        
        video_url = suitable_file.get('link')
        print(f"📥 Downloading video from Pexels...")
        print(f"   Quality: {suitable_file.get('quality')}, Size: {suitable_file.get('width')}x{suitable_file.get('height')}")
        
        # Download the video
        video_response = requests.get(video_url, stream=True, timeout=30)
        video_response.raise_for_status()
        
        # Save to file
        with open(output_file, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✅ Video downloaded successfully: {output_file} ({file_size_mb:.1f} MB)")
        print(f"   Video by: {video.get('user', {}).get('name', 'Unknown')}")
        print(f"   Video URL: {video.get('url')}")
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading from Pexels: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_random_query() -> str:
    """
    Returns a random search query for variety.
    All queries are chosen to avoid copyright issues.
    """
    import random
    
    queries = [
        "abstract moving background",
        "colorful particles",
        "geometric shapes",
        "flowing liquid",
        "light patterns",
        "digital background",
        "minimalist motion",
        "gradient waves",
        "neon lights",
        "space particles"
    ]
    
    return random.choice(queries)


if __name__ == "__main__":
    # Test the downloader
    print("Testing Pexels video downloader...")
    query = get_random_query()
    result = download_pexels_video(query=query)
    if result:
        print(f"\n✅ Test successful! Video saved to: {result}")
    else:
        print("\n❌ Test failed. Make sure PEXELS_API_KEY is set.")
