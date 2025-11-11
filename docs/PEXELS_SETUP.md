# Quick Start: Pexels API Setup

## What is Pexels?

Pexels is a **free stock photo and video platform** with a generous API. The V3 bot uses Pexels for copyright-free background videos.

## Why Pexels?

- ✅ **100% Free** - 20,000 API requests per month, no credit card required
- ✅ **No Copyright Issues** - All videos are free to use, even commercially
- ✅ **No Attribution Required** - Though appreciated
- ✅ **High Quality** - Professional stock videos in HD
- ✅ **Portrait Orientation** - Perfect for 9:16 YouTube Shorts
- ✅ **Variety** - Millions of videos across all categories

## Getting Your API Key

### Step 1: Create Pexels Account
1. Go to https://www.pexels.com
2. Click "Sign Up" (top right)
3. Create account with email or social login

### Step 2: Generate API Key
1. Go to https://www.pexels.com/api/
2. Click "Get Started" or "API" in navigation
3. Click "Your API Key" or "Generate API Key"
4. Copy your API key (looks like: `563492ad6f917000010000015f2d4f1a4ad248e6b31a8f14e5c31d5d`)

### Step 3: Add to GitHub Secrets

1. Go to your repository: `https://github.com/YOUR_USERNAME/reddit-shorts-bot`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PEXELS_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

### Step 4: Test Locally (Optional)

```bash
# Set environment variable
export PEXELS_API_KEY="your_api_key_here"

# Test the downloader
python pexels_downloader.py
```

You should see:
```
🎬 Searching Pexels for: abstract particles
   Found 15 videos
🎬 Downloading video: [URL]
   Saving to: background.mp4
✅ Download complete: background.mp4
   File size: 5.23 MB
```

## Usage in Bot

The bot automatically uses `PEXELS_API_KEY` from environment variables:

```python
from pexels_downloader import download_pexels_video, get_random_query

# Random query for variety
query = get_random_query()  # Returns: abstract, particles, geometric, etc.

# Download background
background = download_pexels_video(
    query=query,
    output_file="background.mp4"
)
```

## API Limits

**Free Tier:**
- 20,000 requests per month
- 200 requests per hour
- No expiration

**Rate Limiting:**
- If you exceed limits, API returns HTTP 429 (Too Many Requests)
- Bot runs every 6 hours = ~120 requests/month = Well within limits!

## Search Queries

The bot includes 10 copyright-safe queries:

1. `abstract particles` - Colorful particle animations
2. `geometric shapes` - Minimalist geometric patterns
3. `flowing liquid` - Fluid motion backgrounds
4. `nature timelapse` - Nature scenes
5. `city lights` - Urban nightscape
6. `bokeh lights` - Defocused light patterns
7. `smoke motion` - Smoke/fog effects
8. `underwater ocean` - Ocean scenes
9. `space stars` - Space/cosmos visuals
10. `gradient background` - Smooth gradient transitions

You can customize queries in `pexels_downloader.py`:

```python
CUSTOM_QUERIES = [
    "your custom query 1",
    "your custom query 2",
    "your custom query 3"
]
```

## Troubleshooting

### Error: "PEXELS_API_KEY environment variable not set"
- **Cause:** API key not configured
- **Fix:** Set `PEXELS_API_KEY` in GitHub Secrets or local environment

### Error: "401 Unauthorized"
- **Cause:** Invalid API key
- **Fix:** Check key is correct, regenerate if needed at pexels.com/api

### Error: "429 Too Many Requests"
- **Cause:** Exceeded rate limit (200/hour or 20,000/month)
- **Fix:** Wait for rate limit reset, or upgrade to paid plan

### Error: "No portrait videos found"
- **Cause:** Search query returned no vertical videos
- **Fix:** Bot will automatically try another query

### Downloads Very Slowly
- **Cause:** Large video files (5-20 MB)
- **Fix:** This is normal, GitHub Actions has good bandwidth

## Alternative: Manual Video Download

If you prefer to use your own background videos:

1. Download any video manually
2. Rename to `background.mp4`
3. Place in project root
4. Bot will use existing file if present

## Pexels API Documentation

Full API docs: https://www.pexels.com/api/documentation/

**Video Search Endpoint:**
```
GET https://api.pexels.com/videos/search?query={query}
```

**Headers:**
```
Authorization: YOUR_API_KEY
```

**Response:**
```json
{
  "page": 1,
  "per_page": 15,
  "total_results": 1000,
  "videos": [
    {
      "id": 123456,
      "width": 1080,
      "height": 1920,
      "duration": 15,
      "video_files": [
        {
          "id": 789,
          "quality": "hd",
          "file_type": "video/mp4",
          "width": 1080,
          "height": 1920,
          "link": "https://..."
        }
      ]
    }
  ]
}
```

## Advanced: Custom Search Logic

Modify `pexels_downloader.py` to customize:

```python
# Filter by duration
def filter_by_duration(videos, min_duration=10, max_duration=60):
    return [v for v in videos if min_duration <= v['duration'] <= max_duration]

# Filter by resolution
def filter_by_resolution(videos, min_width=1080):
    return [v for v in videos if v['width'] >= min_width]

# Search specific user
params = {"query": query, "per_page": 15, "user_id": 12345}
```

## Support

- **Pexels Support:** support@pexels.com
- **API Status:** https://status.pexels.com
- **Community:** https://www.pexels.com/community

---

## Summary

1. ✅ Sign up at pexels.com
2. ✅ Get API key from pexels.com/api
3. ✅ Add `PEXELS_API_KEY` to GitHub Secrets
4. ✅ Bot automatically downloads backgrounds every run
5. ✅ No cost, no attribution required, 20k requests/month

**That's it! Your bot now has professional, copyright-free backgrounds! 🎉**
