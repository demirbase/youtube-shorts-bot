# V3 Implementation Guide - Turkish Specification

## Overview

This is the **V3 implementation** of the Reddit-to-YouTube Shorts bot, following the Turkish specification document. It replaces fragile dependencies with professional, stable alternatives.

## Architecture Changes

### Old V2 Approach
- ❌ **yt-dlp** for Minecraft videos (copyright risk, fragile)
- ❌ **wkhtmltoimage** or **PIL** for generated images (not authentic)
- ❌ **MoviePy** for assembly (slower)
- ❌ **No subtitles**

### New V3 Approach
- ✅ **Pexels API** for free, copyright-safe background videos (20k requests/month)
- ✅ **Playwright** for real Reddit screenshot capture (authentic appearance)
- ✅ **edge-tts** with .srt subtitle generation
- ✅ **FFmpeg filter_complex** for professional multi-layer compositing

## New Modules

### 1. `pexels_downloader.py`
Downloads copyright-free background videos from Pexels Video API.

**Key Features:**
- Free API with 20,000 requests/month (no credit card)
- Searches for portrait-oriented (9:16) videos
- Quality filtering (small/medium/large)
- Random query selection for variety
- 10 copyright-safe search terms (abstract, particles, geometric, etc.)

**Usage:**
```python
from pexels_downloader import download_pexels_video

background = download_pexels_video(
    query="abstract particles",
    output_file="background.mp4"
)
```

**Required Environment Variable:**
```bash
export PEXELS_API_KEY="your_api_key_here"
```

Get your free API key at: https://www.pexels.com/api/

---

### 2. `reddit_screenshot.py`
Captures authentic screenshots of Reddit posts using Playwright headless browser.

**Key Features:**
- Real Reddit appearance (not generated images)
- Headless Chromium browser
- Mobile viewport for vertical format (1080x1920)
- Auto-dismisses cookie banners and popups
- Multiple selector strategies (Reddit HTML changes frequently)
- Fallback to full-page screenshot

**Usage:**
```python
from reddit_screenshot import take_reddit_screenshot

screenshot = take_reddit_screenshot(
    post_url="https://reddit.com/r/AskReddit/comments/...",
    output_file="post.png",
    width=1080,
    height=1920
)
```

**System Requirements:**
- Playwright Python package
- Chromium browser (installed via `playwright install chromium`)
- System dependencies (see GitHub Actions setup)

---

### 3. `subtitle_generator.py`
Generates audio with edge-tts AND creates synchronized .srt subtitle files.

**Key Features:**
- edge-tts for natural text-to-speech
- +30% speed rate (1.3x like V2 audio_utils)
- Extracts WordBoundary timing from edge-tts stream
- Groups words into readable subtitle chunks (4 words per entry)
- SRT format with proper timestamps
- Multiple voice presets (male/female, US/UK/AU)

**Usage:**
```python
from subtitle_generator import generate_audio_with_subtitles_sync, VOICE_PRESETS

audio, subs = generate_audio_with_subtitles_sync(
    text="Your narration text here",
    audio_file="audio.mp3",
    subtitle_file="subtitles.srt",
    voice=VOICE_PRESETS["male_en"],
    rate="+30%"
)
```

**Available Voices:**
- `male_en`, `female_en` (US English)
- `male_uk`, `female_uk` (British English)
- `male_au`, `female_au` (Australian English)
- `male_deep`, `female_young` (alternative styles)

---

### 4. `ffmpeg_composer.py`
Assembles final video using FFmpeg filter_complex for professional multi-layer compositing.

**Key Features:**
- 4-layer composition: Background → Screenshot → Subtitles → Audio
- FFmpeg filter_complex (faster than MoviePy)
- Scale/crop background to 9:16 (1080x1920)
- Overlay screenshot at configurable position (top/center/bottom)
- Burn subtitles with styling (white text, black outline, bottom alignment)
- H.264 video codec with quality settings (CRF 23)
- AAC audio codec (192k bitrate)
- `-shortest` flag for automatic duration matching

**Usage:**
```python
from ffmpeg_composer import compose_video_with_ffmpeg

final_video = compose_video_with_ffmpeg(
    background_video="background.mp4",
    screenshot_image="post.png",
    subtitle_file="subtitles.srt",
    audio_file="audio.mp3",
    output_file="final_short.mp4",
    screenshot_position="top"  # or "center" or "bottom"
)
```

**Filter Chain:**
1. Scale background to 9:16 with cropping
2. Scale screenshot to 90% width
3. Overlay screenshot at specified position
4. Burn subtitles with professional styling
5. Add audio track
6. Output with H.264/AAC encoding

---

## Workflow

The V3 workflow is orchestrated by `main_v3.py`:

```
1. CRON Trigger → Start
   ↓
2. Reddit Scrape (reddit_scraper.py)
   ↓
3. Pexels Video Download (pexels_downloader.py)
   ↓
4. Playwright Screenshot (reddit_screenshot.py)
   ↓
5. edge-tts with Subtitles (subtitle_generator.py)
   ↓
6. FFmpeg filter_complex Assembly (ffmpeg_composer.py)
   ↓
7. YouTube Upload (youtube_uploader.py)
```

## GitHub Actions Setup

The `.github/workflows/bot.yml` file has been updated with:

### New Steps

```yaml
- name: 4. Install System Dependencies for Playwright
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
      libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
      libxdamage1 libxfixes3 libxrandr2 libgbm1 \
      libasound2

- name: 6. Install Playwright Browsers
  run: |
    playwright install chromium --with-deps
```

### New Environment Variables

You must add these secrets in GitHub Settings → Secrets → Actions:

1. **PEXELS_API_KEY** - Your Pexels API key (free at pexels.com/api)

Existing secrets remain:
- CLIENT_SECRETS (YouTube OAuth)
- YOUTUBE_TOKEN (YouTube OAuth)
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USERNAME
- REDDIT_PASSWORD

---

## Requirements

Updated `requirements.txt`:

```
requests
gTTS
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
praw
moviepy
yt-dlp
Pillow
edge-tts          # NEW
playwright        # NEW
```

---

## Testing Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium --with-deps
```

### 2. Set Environment Variables

```bash
export PEXELS_API_KEY="your_key"
export REDDIT_CLIENT_ID="your_id"
export REDDIT_CLIENT_SECRET="your_secret"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
export CLIENT_SECRETS_CONTENT="$(cat CLIENT_SECRETS.json)"
export YOUTUBE_TOKEN_CONTENT="$(cat YOUTUBE_TOKEN.json)"
```

### 3. Test Individual Modules

```bash
# Test Pexels downloader
python pexels_downloader.py

# Test Reddit screenshot (requires Reddit post URL)
python reddit_screenshot.py

# Test subtitle generator
python subtitle_generator.py

# Test FFmpeg composer (requires test files)
python ffmpeg_composer.py
```

### 4. Run Full Bot

```bash
python main_v3.py
```

---

## Risks and Mitigations

### 1. Reddit Policy Risk
**Risk:** Reddit/YouTube may ban bots that republish content  
**Mitigation:**
- Authentic appearance (real screenshots, not scraped text)
- Proper attribution in video description
- SEO optimization encourages organic discovery
- Monitor YouTube Community Guidelines

### 2. Playwright Fragility
**Risk:** Reddit HTML structure changes break selectors  
**Mitigation:**
- Multiple selector strategies (`[data-test-id="post-content"]`, `shreddit-post`, `article`, etc.)
- Fallback to full-page screenshot
- Graceful error handling
- User-Agent rotation if needed

### 3. edge-tts Stability
**Risk:** edge-tts uses reverse-engineered Microsoft API  
**Mitigation:**
- Simple fallback: edge-tts → gTTS (no subtitles but working audio)
- edge-tts author warns against production use, but widely used
- Monitor for Microsoft API changes
- Consider paid TTS service for production (Google Cloud TTS, Amazon Polly)

### 4. GitHub Actions Complexity
**Risk:** Playwright setup requires many system dependencies  
**Mitigation:**
- Documented apt-get install commands
- `playwright install --with-deps` handles most dependencies
- Test in GitHub Actions before deploying
- Fallback: Run bot locally, upload manually

---

## Performance

**V2 (Old):**
- Video creation: ~2-3 minutes (MoviePy encoding)
- Fragile dependencies: wkhtmltoimage, yt-dlp

**V3 (New):**
- Video creation: ~1-2 minutes (FFmpeg filter_complex is faster)
- Playwright adds ~10 seconds for screenshot capture
- More reliable: No copyright issues, authentic appearance

---

## Migration Notes

### Old V2 Files (Deprecated)
- `background_downloader.py` → Replaced by `pexels_downloader.py`
- `comment_image_generator.py` → Replaced by `reddit_screenshot.py`
- `comment_image_pil.py` → Replaced by `reddit_screenshot.py`
- `video_assembler_v2.py` → Replaced by `ffmpeg_composer.py`
- `main_v2.py` → Replaced by `main_v3.py`

### Still Used
- `reddit_scraper.py` (Reddit API integration)
- `youtube_uploader.py` (YouTube upload)
- `audio_utils.py` (speed_up_audio for post-processing if needed)

### New Entry Point
- `main.py` now imports and runs `main_v3.main()`

---

## Troubleshooting

### Playwright Installation Issues
```bash
# Manually install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Install Playwright browser
playwright install chromium --with-deps
```

### Reddit Screenshot Failing
- Check if Reddit URL is accessible
- Try `take_reddit_screenshot_simple()` for more reliable (but less targeted) screenshots
- Verify Playwright browser installed: `playwright install chromium`

### edge-tts Not Working
- Fallback to gTTS: `from gtts import gTTS`
- edge-tts requires internet connection to Microsoft servers
- Check for edge-tts updates: `pip install --upgrade edge-tts`

### Pexels API Issues
- Verify API key: `echo $PEXELS_API_KEY`
- Check rate limits: 20,000 requests/month (free tier)
- Test with curl: `curl -H "Authorization: YOUR_KEY" https://api.pexels.com/videos/search?query=abstract`

---

## Future Improvements

1. **Voice Variety**: Rotate between different edge-tts voices for each video
2. **Dynamic Positioning**: Adjust screenshot position based on post length
3. **Thumbnail Generation**: Extract frame from video for custom thumbnail
4. **Comment Highlighting**: Add visual effects to emphasize funny comments
5. **Music Background**: Add subtle background music under narration
6. **Multi-Language**: Support non-English subreddits with language detection
7. **A/B Testing**: Try different background styles, subtitle fonts, etc.

---

## Credits

- **Pexels API**: Free video backgrounds (https://www.pexels.com)
- **Playwright**: Browser automation (https://playwright.dev)
- **edge-tts**: Microsoft Edge TTS (https://github.com/rany2/edge-tts)
- **FFmpeg**: Video processing (https://ffmpeg.org)
- **PRAW**: Reddit API wrapper (https://praw.readthedocs.io)
- **Google API**: YouTube Data API (https://developers.google.com/youtube/v3)

---

## License

Same as main project license.
