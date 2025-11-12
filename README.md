# Reddit-to-YouTube Shorts Bot 🤖 (V4)

A **100% free**, fully automated content pipeline that converts top Reddit posts into engaging YouTube Shorts with **dynamic backgrounds**, **karaoke-style subtitles**, and **professional Reddit UI**.

## 🎯 What This Bot Does

1. **Fetches** top posts from r/AskReddit using Reddit's official API (PRAW)
2. **Downloads** random copyright-free background videos from Pexels API (20+ categories)
3. **Creates** authentic Reddit UI frame with PIL (transparent text area for subtitles)
4. **Generates** AI voice narration with edge-tts (Microsoft voices)
5. **Syncs** karaoke-style subtitles that appear as words are spoken
6. **Composes** 4-layer videos using FFmpeg filter_complex (background + frame + subtitles + audio)
7. **Uploads** to YouTube as public Shorts with automatic metadata
8. **Runs automatically** via GitHub Actions (manual or scheduled)
9. **Tracks used posts** to prevent duplicates

## 🆕 V4 Architecture (Multi-Layer Composite)

**Revolutionary 4-Layer Video System:**
```
Layer 1: Dynamic Background (Pexels video - different every time)
Layer 2: Reddit UI Frame (PIL-generated, transparent text area)
Layer 3: Karaoke Subtitles (FFmpeg burned, synced with audio)
Layer 4: Audio Track (edge-tts with sentence-level timing)
```

**Key Features:**
- 🎬 **Dynamic Backgrounds** - 20+ categories (gaming, ASMR, nature, abstract, sports, etc.)
- 🎤 **Karaoke-Style Text** - Subtitles appear synchronized with voice narration
- 📱 **Reddit UI** - Authentic Reddit post appearance with customizable styling
- 🔄 **Question → Answer Flow** - Title displays first, then top comments
- 🎨 **Fully Customizable** - 90+ config parameters for colors, fonts, layout

**V4 vs V3 Comparison:**
- ❌ V3: Static PIL image with text burned in, looped over audio
- ✅ V4: Dynamic video background + transparent frame + live subtitle burn
- ❌ V3: Same Minecraft video every time
- ✅ V4: Different Pexels video each run (20+ categories)
- ❌ V3: All text visible at once
- ✅ V4: Text appears as spoken (karaoke-style)

## ✅ Current Status

**V4 fully implemented and production-ready!** All components:
- ✅ Reddit API authentication (PRAW)
- ✅ Pexels API integration (20+ dynamic categories)
- ✅ PIL Reddit frame generator (transparent + customizable)
- ✅ edge-tts with sentence-level subtitle generation
- ✅ FFmpeg 4-layer filter_complex composition
- ✅ YouTube API authentication
- ✅ GitHub Actions automation
- ✅ Complete documentation

## 🚀 Quick Start

### 1. Prerequisites

**Accounts needed:**
- Reddit account (for API access)
- Google account (for YouTube uploads)
- GitHub account (for automation)

**Local setup (one-time):**
- Python 3.10+
- FFmpeg installed

### 2. Setup Steps

1. **Fork/Clone this repository**
   ```bash
   git clone https://github.com/demirbase/youtube-shorts-bot
   cd youtube-shorts-bot
   ```

2. **Set up Reddit API**
   - Follow the guide: [`docs/REDDIT_API_SETUP.md`](docs/REDDIT_API_SETUP.md)
   - Add 4 GitHub secrets: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`

3. **Set up Pexels API**
   - Follow the guide: [`docs/PEXELS_SETUP.md`](docs/PEXELS_SETUP.md)
   - Get free API key (20,000 requests/month)
   - Add GitHub secret: `PEXELS_API_KEY`

4. **Set up YouTube API**
   - Create Google Cloud project
   - Enable YouTube Data API v3
   - Download credentials as `client_secrets.json`
   - Run `python authenticate.py` locally to generate `token.json`
   - Add 2 GitHub secrets with file contents: `CLIENT_SECRETS_CONTENT`, `YOUTUBE_TOKEN_CONTENT`

5. **Enable GitHub Actions**
   - Go to **Actions** tab in your repo
   - Enable workflows
   - Run manually via "Run workflow" button (schedule disabled by default)

### 3. Manual Testing

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_secret"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
export PEXELS_API_KEY="your_pexels_key"
export CLIENT_SECRETS_CONTENT="$(cat client_secrets.json)"
export YOUTUBE_TOKEN_CONTENT="$(cat token.json)"

# Run the bot
python main.py

# Or test specific modules
python test_v4_architecture.py  # Test V4 pipeline
```

## 📁 Project Structure

```
reddit-shorts-bot/
├── main.py                      # Entry point (runs main_v4.py)
├── main_v4.py                   # V4 orchestration (6-step pipeline)
│
├── V4 Core Modules:
├── reddit_fetcher.py            # PRAW wrapper for Reddit API
├── pexels_dynamic.py            # Downloads random background videos
├── reddit_frame_creator.py      # Creates transparent Reddit UI frame
├── reddit_image_config.py       # 90+ customization parameters
├── subtitle_generator_v2.py     # Generates audio + synced subtitles
├── ffmpeg_composer_v2.py        # 4-layer video composition
│
├── Supporting Files:
├── authenticate.py              # One-time YouTube OAuth
├── youtube_uploader.py          # YouTube API upload handler
├── requirements.txt             # Python dependencies
├── used_posts.txt               # Tracks processed posts
│
├── .github/workflows/
│   └── bot.yml                 # GitHub Actions automation
│
├── docs/                        # Documentation
│   ├── V4_ARCHITECTURE.md      # Technical V4 guide
│   ├── CUSTOMIZE_IMAGE.md      # Customization guide
│   ├── REDDIT_API_SETUP.md     # Reddit setup
│   ├── PEXELS_SETUP.md         # Pexels API guide
│   └── TROUBLESHOOTING.md      # Common issues
│
└── legacy/                      # Old V1/V2/V3 files (archived)
```

## ⚙️ Configuration

### Visual Customization

Edit `reddit_image_config.py` to customize Reddit UI appearance (90+ parameters):

```python
# Colors
COLORS = {
    'bg': (30, 30, 30),           # Dark background
    'upvote': (255, 69, 0),       # Reddit orange
    'username': (135, 206, 250),  # Light blue
    # ... and many more
}

# Fonts & Layout
FONTS = {
    'title': ('Arial Bold', 42),
    'username': ('Arial', 32),
    # ...
}
```

See [`docs/CUSTOMIZE_IMAGE.md`](docs/CUSTOMIZE_IMAGE.md) for full guide.

### Bot Configuration

Edit `main_v4.py` to customize bot behavior:

```python
SUBREDDIT = "AskReddit"                    # Source subreddit
MIN_COMMENTS = 5                            # Minimum comment count
VIDEO_TITLE_PREFIX = "Reddit Story: "       # Video title format
```

### GitHub Actions Schedule

Edit `.github/workflows/bot.yml` to change automation:

```yaml
# Currently: Manual trigger only (workflow_dispatch)
# To enable automatic runs, uncomment:
# schedule:
#   - cron: '0 */6 * * *'  # Every 6 hours
```

## 🔧 How It Works (V4 Pipeline)

### 6-Step Workflow

1. **Fetch Reddit Post** (`reddit_fetcher.py`)
   - Authenticates with PRAW
   - Finds unused post from r/AskReddit
   - Filters by comment count and length
   - Marks post as used

2. **Generate Audio + Subtitles** (`subtitle_generator_v2.py`)
   - Creates question → answer flow
   - Generates TTS with edge-tts (Microsoft voices)
   - Produces sentence-level .srt subtitles
   - Syncs timing with audio

3. **Download Background Video** (`pexels_dynamic.py`)
   - Randomly selects category (gaming, ASMR, nature, etc.)
   - Searches Pexels API with category-specific queries
   - Downloads copyright-free video
   - Different background every run

4. **Create Reddit Frame** (`reddit_frame_creator.py`)
   - Generates Reddit UI with PIL
   - Uses `reddit_image_config.py` for styling
   - Creates transparent text area for subtitles
   - Outputs RGBA PNG (1080x1920)

5. **Compose Video** (`ffmpeg_composer_v2.py`)
   - 4-layer FFmpeg filter_complex:
     - Layer 1: Background video (scaled + cropped)
     - Layer 2: Reddit frame overlay
     - Layer 3: Karaoke subtitles (burned in)
     - Layer 4: Audio sync
   - Outputs final 9:16 MP4

6. **Upload to YouTube** (`youtube_uploader.py`)
   - Authenticates with YouTube API
   - Uploads as public Short
   - Sets title, description, tags
   - Handles quota exceeded gracefully

### Key Features
- **Duplicate prevention**: Tracks used post IDs in `used_posts.txt`
- **Dynamic content**: Different background video every run
- **Flow-based narration**: Question first, then answers with pauses
- **Error handling**: Graceful failures with detailed logging
- **Quota management**: Saves videos locally if YouTube quota exceeded

## ⚠️ Important Warnings

### 1. YouTube API Quota
- **10,000 units/day** limit (default)
- **1,600 units per upload**
- **Maximum 6 videos/day**
- Current schedule (4x/day) is safe

### 2. Pexels API Limits
- **20,000 requests/month** (free tier)
- ~666 videos per day possible
- Attribution not required but encouraged
- Current usage: 1 request per video

### 3. Content Policy
YouTube considers automated, repetitive content as "low-effort":
- May not be eligible for monetization
- Risk of demonetization after review
- Potential spam violations

**This is a learning project, not a monetization strategy.**

### 4. Dependencies
- **Reddit API**: Official PRAW library (stable)
- **Pexels API**: Free video API with 20k/month limit (stable)
- **edge-tts**: Microsoft Text-to-Speech (stable, free)
- **YouTube API**: Official Google library (stable)
- **FFmpeg**: Open-source video tool (stable)
- **Pillow (PIL)**: Image generation library (stable)

All dependencies are production-ready and reliable.

## 📚 Documentation

### Setup Guides
- **[Reddit API Setup](docs/REDDIT_API_SETUP.md)** - Complete Reddit app configuration
- **[Pexels API Setup](docs/PEXELS_SETUP.md)** - Get free API key for backgrounds
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### V4 Documentation
- **[V4 Architecture](docs/V4_ARCHITECTURE.md)** - Technical deep dive into 4-layer system
- **[Customize Image](docs/CUSTOMIZE_IMAGE.md)** - Full guide to Reddit UI customization
- **[V4 Architecture Fix](docs/V4_ARCHITECTURE_FIX.md)** - Why V4 replaced V3

### Legacy Documentation
- **[docs/archive/](docs/archive/)** - V1/V2/V3 documentation and version history

## 🐛 Troubleshooting

### Reddit authentication fails
- Verify credentials in GitHub secrets
- Check Reddit app is type "script"
- Ensure username doesn't include `/u/`

### Pexels download fails
- Verify `PEXELS_API_KEY` secret is set
- Check API quota (20k/month)
- Ensure internet connection in runner

### YouTube upload fails
- Re-run `authenticate.py` locally
- Update `YOUTUBE_TOKEN_CONTENT` secret
- Check API quota hasn't been exceeded

### Video creation fails
- Verify FFmpeg is installed in workflow
- Check edge-tts audio generation logs
- Ensure all temp files are cleaned up

### Subtitle sync issues
- Check subtitle_generator_v2.py timing
- Verify audio file exists before FFmpeg
- Test with test_v4_architecture.py

See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for detailed solutions.

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome! Open an issue to discuss improvements.

## 📜 License

MIT License - feel free to fork and modify for your own use.

## ⭐ Acknowledgments

- **PRAW** - Python Reddit API Wrapper
- **Pexels** - Free stock video API
- **edge-tts** - Microsoft Text-to-Speech
- **Pillow (PIL)** - Python Imaging Library
- **FFmpeg** - Video processing powerhouse
- **Google APIs** - YouTube Data API

---

**Status**: ✅ V4 Working and Production-Ready  
**Last Updated**: November 12, 2025  
**Version**: 4.0 (Multi-Layer Architecture)  
**Maintainer**: [@demirbase](https://github.com/demirbase)
