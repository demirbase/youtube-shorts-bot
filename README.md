# Reddit-to-YouTube Shorts Bot 🤖

A **100% free**, fully automated content pipeline that converts top Reddit posts into YouTube Shorts videos with AI narration.

## 🎯 What This Bot Does

1. **Scrapes** top posts from r/AskReddit using Reddit's official API
2. **Generates** AI voice narration using Google Text-to-Speech
3. **Creates** 9:16 vertical videos with burned-in subtitles
4. **Uploads** to YouTube as private videos
5. **Runs automatically** every 6 hours via GitHub Actions
6. **Tracks used posts** to prevent duplicates

## ✅ Current Status

**Working and tested!** All components are functional:
- ✅ Reddit API authentication
- ✅ Post fetching with duplicate prevention
- ✅ Google TTS audio generation
- ✅ Video creation with FFmpeg
- ✅ YouTube API authentication
- ✅ Automated uploads
- ✅ GitHub Actions automation

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

3. **Set up YouTube API**
   - Create Google Cloud project
   - Enable YouTube Data API v3
   - Download credentials as `client_secrets.json`
   - Run `python authenticate.py` locally to generate `token.json`
   - Add 2 GitHub secrets with file contents: `CLIENT_SECRETS_CONTENT`, `YOUTUBE_TOKEN_CONTENT`

4. **Enable GitHub Actions**
   - Go to **Actions** tab in your repo
   - Enable workflows
   - The bot runs automatically every 6 hours

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
export CLIENT_SECRETS_CONTENT="$(cat client_secrets.json)"
export YOUTUBE_TOKEN_CONTENT="$(cat token.json)"

# Run the bot
python main.py
```

## 📁 Project Structure

```
reddit-shorts-bot/
├── main.py                 # Main orchestration script
├── reddit_scraper.py       # Fetches posts from Reddit
├── video_creator.py        # Generates audio and video
├── youtube_uploader.py     # Handles YouTube uploads
├── authenticate.py         # One-time YouTube OAuth (run locally)
├── requirements.txt        # Python dependencies
├── used_posts.txt          # Tracks processed posts
├── background.png          # Video background (1080x1920)
├── .github/workflows/
│   └── bot.yml            # GitHub Actions automation
└── docs/                   # Documentation
    ├── REDDIT_API_SETUP.md
    ├── TROUBLESHOOTING.md
    └── [other guides]
```

## ⚙️ Configuration

Edit `main.py` to customize:

```python
SUBREDDIT = "AskReddit"                    # Source subreddit
VIDEO_TITLE_PREFIX = "Reddit Asks: "       # Video title format
VIDEO_TAGS = ["reddit", "askreddit", ...]  # YouTube tags
```

Edit `.github/workflows/bot.yml` to change schedule:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (default)
  # - cron: '0 0,12 * * *'  # Twice per day
  # - cron: '0 0 * * *'     # Once per day
```

## 🔧 How It Works

### Workflow
1. **GitHub Actions** triggers on schedule (every 6 hours)
2. **reddit_scraper.py** authenticates with Reddit API and fetches top post
3. **video_creator.py** generates audio with Google TTS and assembles video with FFmpeg
4. **youtube_uploader.py** uploads video to YouTube as private
5. Workflow commits updated `used_posts.txt` to prevent duplicates

### Key Features
- **Duplicate prevention**: Tracks used post IDs in `used_posts.txt`
- **Error handling**: Graceful failures with detailed logging
- **Resumable uploads**: YouTube API supports large file uploads
- **Secure secrets**: All credentials stored as GitHub Actions secrets

## ⚠️ Important Warnings

### 1. YouTube API Quota
- **10,000 units/day** limit (default)
- **1,600 units per upload**
- **Maximum 6 videos/day**
- Current schedule (4x/day) is safe

### 2. Content Policy
YouTube considers automated, repetitive content as "low-effort":
- May not be eligible for monetization
- Risk of demonetization after review
- Potential spam violations

**This is a learning project, not a monetization strategy.**

### 3. Dependencies
- **Reddit API**: Official PRAW library (stable)
- **Google TTS**: Official gTTS library (stable)
- **YouTube API**: Official Google library (stable)
- **FFmpeg**: Open-source video tool (stable)

All dependencies are production-ready and reliable.

## 📚 Documentation

- **[Reddit API Setup Guide](docs/REDDIT_API_SETUP.md)** - Complete Reddit app configuration
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Fix History](docs/)** - Documentation of past issues and fixes

## 🐛 Troubleshooting

### Reddit authentication fails
- Verify credentials in GitHub secrets
- Check Reddit app is type "script"
- Ensure username doesn't include `/u/`

### YouTube upload fails
- Re-run `authenticate.py` locally
- Update `YOUTUBE_TOKEN_CONTENT` secret
- Check API quota hasn't been exceeded

### Video creation fails
- Ensure `background.png` exists (1080x1920)
- Verify FFmpeg is installed in workflow
- Check audio generation logs

See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for detailed solutions.

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome! Open an issue to discuss improvements.

## 📜 License

MIT License - feel free to fork and modify for your own use.

## ⭐ Acknowledgments

- **PRAW** - Python Reddit API Wrapper
- **gTTS** - Google Text-to-Speech
- **FFmpeg** - Video processing
- **Google APIs** - YouTube Data API

---

**Status**: ✅ Working and tested  
**Last Updated**: November 10, 2025  
**Maintainer**: [@demirbase](https://github.com/demirbase)
