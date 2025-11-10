# Reddit-to-YouTube Shorts Bot

An **100% free**, fully automated content pipeline that converts top Reddit posts into YouTube Shorts videos. This system uses GitHub Actions for compute and scheduling, scrapes Reddit's public endpoints, generates speech with Microsoft Edge TTS, and uploads to YouTube via the official API.

## 🎯 What This Bot Does

1. **Scrapes** top posts from r/AskReddit (configurable)
2. **Generates** AI voice narration using Microsoft Edge TTS
3. **Creates** 9:16 vertical videos with subtitles burned in
4. **Uploads** to YouTube as private videos
5. **Runs automatically** every 6 hours via GitHub Actions
6. **Tracks state** to prevent duplicate content

## ⚠️ Critical Warnings

Before using this system, understand these risks:

### 1. **Fragile Architecture**
- **Reddit Scraping**: Uses unofficial `.json` endpoints that can be rate-limited or blocked at any time
- **Edge TTS**: Relies on an unofficial, reverse-engineered library that Microsoft can break at any moment
- **YouTube Policy**: This type of automated, AI-generated content is considered "low-effort" and risks demonetization

### 2. **YouTube API Quota Limits**
- Default quota: **10,000 units/day**
- Upload cost: **1,600 units/video**
- **Maximum: 6 uploads per day**
- The current 4x/day schedule is safe, but don't increase frequency

### 3. **Monetization Risk**
YouTube actively enforces policies against mass-produced, repetitive content. Channels using this type of automation have a high risk of:
- Never achieving monetization eligibility
- Being demonetized after review
- Having videos removed for spam

**This is a learning/experimental project, not a reliable business model.**

---

## 📋 Prerequisites

### Local Machine (One-Time Setup)
- **Python 3.10+**
- **FFmpeg** installed and in PATH
- A **Google Account** with access to a YouTube channel

### GitHub Account
- A **GitHub account** (free tier is sufficient)
- Ability to create public repositories (required for free GitHub Actions)

---

## 🚀 Complete Setup Guide

### Phase 1: Google Cloud Console Setup

#### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown (top left) → **New Project**
3. Name it (e.g., "YouTube-Bot-Project") → **Create**

#### 1.2 Enable YouTube Data API v3
1. In the search bar, type "YouTube Data API v3"
2. Click on it → Click **Enable**

#### 1.3 Configure OAuth Consent Screen
1. Navigate to **APIs & Services** → **OAuth consent screen** (left sidebar)
2. Select **External** → Click **Create**
3. Fill in required fields:
   - **App name**: e.g., "Reddit Bot"
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **Save and Continue**
5. On "Scopes" page:
   - Click **Add or Remove Scopes**
   - Search for "YouTube Data API v3"
   - Check the box for `.../auth/youtube.upload`
   - Click **Update** → **Save and Continue**
6. On "Test users" page:
   - Click **Add Users**
   - Enter the Gmail address that owns your YouTube channel
   - Click **Add** → **Save and Continue**
7. Click **Back to Dashboard**

#### 1.4 Create OAuth 2.0 Credentials
1. Navigate to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. Choose **Application type**: **Desktop app**
4. Name it (e.g., "Bot-Desktop-Client") → **Create**
5. A popup appears → Click **Download JSON**
6. **Rename** the downloaded file to `client_secrets.json`

✅ **Save this file securely** - you'll need it in the next phase.

---

### Phase 2: Local Authentication

This generates your YouTube API refresh token.

#### 2.1 Set Up Local Project
```bash
# Clone or download this repository
cd reddit-shorts-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2.2 Add Your Files
1. Place `client_secrets.json` (from Phase 1) in the project root
2. Add a `background.png` image (1080x1920 pixels, 9:16 aspect ratio)
   - See `BACKGROUND_README.md` for recommendations

#### 2.3 Run Authentication Script
```bash
python authenticate.py
```

**What happens:**
1. Your browser opens automatically
2. Log in with the Google Account you added as a "Test user"
3. You'll see "Google hasn't verified this app" → Click **Advanced** → **Go to [app name] (unsafe)**
4. Grant permission to "Upload videos to your YouTube channel"
5. Browser shows "Authentication successful"
6. A `token.json` file is created in your project folder

✅ **You now have both secrets needed for GitHub Actions**

---

### Phase 3: GitHub Repository Setup

#### 3.1 Create GitHub Repository
1. Go to [GitHub](https://github.com) and create a **new public repository**
   - Name: e.g., "youtube-shorts-bot"
   - **Must be public** for free GitHub Actions

#### 3.2 Push Code to GitHub
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial bot setup"
git branch -M main

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 3.3 Add GitHub Secrets
1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**

**Secret 1: CLIENT_SECRETS**
- Name: `CLIENT_SECRETS`
- Value: Open `client_secrets.json` in a text editor, copy the **entire contents** (from `{` to `}`), paste into the secret field
- Click **Add secret**

**Secret 2: YOUTUBE_TOKEN**
- Click **New repository secret** again
- Name: `YOUTUBE_TOKEN`
- Value: Open `token.json`, copy the **entire contents**, paste into the secret field
- Click **Add secret**

🔒 **Security Note**: Never commit these files to git. The `.gitignore` file already excludes them.

---

### Phase 4: Activation

#### 4.1 Verify Files Are Pushed
Ensure these files are in your GitHub repository:
```
reddit-shorts-bot/
├── .github/
│   └── workflows/
│       └── bot.yml
├── authenticate.py
├── main.py
├── reddit_scraper.py
├── video_creator.py
├── youtube_uploader.py
├── requirements.txt
├── .gitignore
├── used_posts.txt
├── background.png  ← YOU MUST ADD THIS
└── README.md
```

#### 4.2 Manual Test Run
1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Click **Reddit-to-YouTube-Shorts-Bot** workflow (left sidebar)
4. Click **Run workflow** (right side) → **Run workflow**
5. Click on the running job to watch real-time logs

#### 4.3 Verify Success
✅ **On GitHub**: Check your repository's commit history for a new "AUTOBOT: Update used_posts.txt" commit

✅ **On YouTube**: Go to [YouTube Studio](https://studio.youtube.com) → **Content** tab → You should see a new private video

---

## 🤖 How It Works

### Automation Schedule
The workflow runs **automatically every 6 hours** (00:00, 06:00, 12:00, 18:00 UTC).

You can also trigger it manually from the Actions tab.

### What Happens Each Run
1. ✅ GitHub Actions runner starts
2. ✅ Checks out your repository code
3. ✅ Installs Python dependencies and FFmpeg
4. ✅ Loads your secrets from GitHub Actions secrets
5. ✅ Scrapes r/AskReddit for a new top post
6. ✅ Generates audio narration with Edge TTS
7. ✅ Creates subtitles and assembles video with FFmpeg
8. ✅ Uploads video to YouTube as "Private"
9. ✅ Updates `used_posts.txt` to prevent duplicates
10. ✅ Commits the updated state file back to GitHub

---

## ⚙️ Configuration

### Change Subreddit
Edit `main.py`:
```python
SUBREDDIT = "AskReddit"  # Change to any subreddit
```

### Change Upload Schedule
Edit `.github/workflows/bot.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # Examples:
  # '0 */12 * * *'  → Every 12 hours
  # '0 0 * * *'     → Once per day at midnight UTC
```

⚠️ **Warning**: Don't increase frequency beyond 6x/day due to YouTube API quota limits (max 6 uploads/day).

### Change Video Privacy
Edit `youtube_uploader.py`:
```python
"privacyStatus": "private"  # Options: "public", "private", "unlisted"
```

### Change TTS Voice
Edit `video_creator.py`:
```python
VOICE = "en-US-JennyNeural"  # See Microsoft Edge TTS voices list
```

Available voices: https://github.com/rany2/edge-tts#voice-list

---

## 📊 YouTube API Quota Budget

| Action | Quota Cost | Daily Max (if only this action) |
|--------|-----------|--------------------------------|
| Upload Video | 1,600 | 6 uploads |
| Search | 100 | 100 searches |
| Add to Playlist | 50 | 200 additions |
| List Playlists | 1 | 10,000 lists |

**Your daily budget: 10,000 units**

Current schedule (4 uploads/day) uses: **6,400 units/day** (64% of quota)

---

## 🐛 Troubleshooting

### "No new post found or scraping failed"
- Reddit may be rate-limiting your IP
- Try reducing the schedule frequency
- Reddit's `.json` endpoint may have changed

### "YouTube authentication failed"
- Verify both secrets are correctly added in GitHub Settings → Secrets
- Ensure you copied the **entire JSON content** including braces `{ }`
- Re-run `authenticate.py` locally to generate a fresh `token.json`

### "Video creation failed"
- Ensure `background.png` exists in your repository
- Check GitHub Actions logs for FFmpeg errors
- Verify FFmpeg is set up correctly in the workflow

### "Quota exceeded" error
- You've hit YouTube's 10,000 unit daily limit
- Wait 24 hours for quota reset (resets at midnight Pacific Time)
- Consider reducing upload frequency

### Edge TTS stops working
- Microsoft may have changed their internal API
- Check [edge-tts GitHub issues](https://github.com/rany2/edge-tts/issues)
- This is expected - see "Fragile Architecture" warning

---

## 🎓 Learning Resources

### Understanding the Code
- `authenticate.py`: OAuth 2.0 flow for local token generation
- `reddit_scraper.py`: HTTP requests to Reddit's JSON endpoints
- `video_creator.py`: Async TTS generation and FFmpeg video assembly
- `youtube_uploader.py`: Google API client for authenticated uploads
- `main.py`: Orchestration layer tying all modules together

### Key Technologies
- **GitHub Actions**: CI/CD automation platform
- **Edge TTS**: Unofficial Microsoft TTS wrapper
- **FFmpeg**: Media processing framework
- **YouTube Data API v3**: Official Google API

---

## 📈 Scaling to Production (Paid)

To make this system robust, replace the free components:

### 1. Replace Edge TTS
- ✅ **Azure Cognitive Services** (official Microsoft TTS): $4-16 per million characters
- ✅ **ElevenLabs**: $5-330/month for high-quality voices
- ✅ **Google Cloud Text-to-Speech**: $4-16 per million characters

### 2. Replace Reddit Scraping
- ✅ Register for **official Reddit API** (free, but requires authentication)
- ✅ Rate limit: 600 requests per 10 minutes (vs. ~20 for public endpoint)

### 3. Address YouTube Policies
- ✅ Add **unique value**: Commentary, editing, visualizations
- ✅ Replace static image with **dynamic B-roll footage**
- ✅ Add **human voiceover** or personality
- ✅ Focus on **original insight** rather than content aggregation

---

## 📝 License

This project is provided as-is for educational purposes. 

**Important Legal Notes**:
- Reddit's Terms of Service prohibit automated scraping without permission
- YouTube's Terms of Service prohibit spam and mass-produced content
- Microsoft Edge TTS is reverse-engineered and not officially supported
- Use at your own risk

---

## 🤝 Contributing

This is an educational/experimental project. Feel free to fork and modify for your own learning.

**Ideas for improvements**:
- Add multiple subreddit support
- Implement video thumbnail generation
- Add webhook notifications (Discord, Slack)
- Create a dashboard for monitoring uploads
- Add error recovery and retry logic

---

## 📧 Support

For issues related to:
- **Google API**: Check [Google's API documentation](https://developers.google.com/youtube/v3)
- **Edge TTS**: See [edge-tts GitHub repo](https://github.com/rany2/edge-tts)
- **GitHub Actions**: Review [GitHub Actions documentation](https://docs.github.com/en/actions)

---

## 🎬 What's Generated

Each video contains:
- 📢 AI voice reading the post title + top 3 comments
- 📝 Auto-generated subtitles burned into the video
- 🖼️ Static background image (1080x1920 vertical format)
- 🎵 192kbps AAC audio
- 📱 Optimized for YouTube Shorts (9:16 aspect ratio)
- 🔒 Uploaded as "Private" by default

---

**Ready to get started?** Follow Phase 1 above! 🚀

---

**Disclaimer**: This system is designed for educational purposes to demonstrate automation concepts. The author is not responsible for any policy violations, API changes, or account restrictions that may result from using this code. Always review and comply with the Terms of Service of all platforms you interact with.
