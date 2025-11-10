# Troubleshooting Guide

## Reddit 403 Blocking Issue

### Problem
When running on GitHub Actions, you may see:
```
Error scraping Reddit: 403 Client Error: Blocked
```

### Why This Happens
1. **GitHub Actions IP Addresses**: Reddit blocks many cloud service IPs, including GitHub Actions runners
2. **Rate Limiting**: Multiple automated requests from the same IP trigger Reddit's anti-bot protection
3. **User-Agent Detection**: Reddit actively blocks requests that look like bots

### Solutions Implemented

The updated `reddit_scraper.py` includes:
- ✅ More realistic browser headers
- ✅ Random delays between requests (1-3 seconds)
- ✅ Fallback to `old.reddit.com` if main site blocks
- ✅ Better error logging

### If It Still Doesn't Work

#### Option 1: Use Reddit's Official API (Recommended)

Reddit's official API is more reliable and has higher rate limits:

1. **Create a Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..." at the bottom
   - Choose "script"
   - Fill in name and redirect URI: `http://localhost:8080`
   - Click "create app"
   - Note your `client_id` and `client_secret`

2. **Add to GitHub Secrets**:
   - Add `REDDIT_CLIENT_ID` secret
   - Add `REDDIT_CLIENT_SECRET` secret
   - Add `REDDIT_USERNAME` secret (your Reddit username)
   - Add `REDDIT_PASSWORD` secret (your Reddit password)

3. **Update requirements.txt**:
   ```
   praw
   ```

4. **Use this alternative `reddit_scraper.py`**:
   ```python
   import praw
   import os
   
   USED_POSTS_FILE = "used_posts.txt"
   
   def get_top_reddit_post(subreddit: str) -> dict | None:
       reddit = praw.Reddit(
           client_id=os.environ.get('REDDIT_CLIENT_ID'),
           client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
           user_agent='python:reddit-shorts-bot:v1.0 (by /u/YOUR_USERNAME)',
           username=os.environ.get('REDDIT_USERNAME'),
           password=os.environ.get('REDDIT_PASSWORD')
       )
       
       if not os.path.exists(USED_POSTS_FILE):
           open(USED_POSTS_FILE, 'w').close()
       
       with open(USED_POSTS_FILE, 'r') as f:
           used_post_ids = set(line.strip() for line in f if line.strip())
       
       for submission in reddit.subreddit(subreddit).top('day', limit=20):
           if submission.id not in used_post_ids and not submission.is_video and not submission.over_18:
               submission.comments.replace_more(limit=0)
               comments = submission.comments.list()[:3]
               
               post_body = "\n\n".join([c.body for c in comments if hasattr(c, 'body')])
               
               if not post_body:
                   continue
               
               with open(USED_POSTS_FILE, 'a') as f:
                   f.write(f"{submission.id}\n")
               
               return {
                   "id": submission.id,
                   "title": submission.title,
                   "body": post_body,
                   "url": f"https://reddit.com{submission.permalink}"
               }
       
       return None
   ```

#### Option 2: Run on Your Own Server

Instead of GitHub Actions, run the bot on:
- A Raspberry Pi at home
- A cheap VPS ($5/month DigitalOcean/Vultr)
- Your personal computer with a cron job

This avoids the shared IP issue entirely.

#### Option 3: Use Different Subreddits

Some subreddits are less protected than r/AskReddit. Try:
- r/CasualConversation
- r/TrueOffMyChest
- r/NoStupidQuestions

Edit `main.py`:
```python
SUBREDDIT = "CasualConversation"  # Less strict than AskReddit
```

#### Option 4: Reduce Frequency

The current schedule (every 6 hours) might be too aggressive. Try:
- Once per day: `cron: '0 0 * * *'`
- Twice per day: `cron: '0 0,12 * * *'`

Edit `.github/workflows/bot.yml` to change the schedule.

---

## YouTube Upload Failures

### "Authentication failed"

**Solution**:
1. Re-run `python authenticate.py` locally
2. Copy the **entire** contents of `token.json` (including `{` and `}`)
3. Update the `YOUTUBE_TOKEN` secret in GitHub
4. Ensure `CLIENT_SECRETS` secret is also set correctly

### "Quota exceeded"

**Solution**:
- You've used your 10,000 daily units (6 uploads)
- Wait until midnight Pacific Time for quota reset
- Reduce upload frequency in workflow schedule

---

## Video Creation Failures

### "background.png not found"

**Solution**:
- Ensure `background.png` exists in repository root
- Check it's committed: `git add background.png && git commit && git push`

### FFmpeg errors

**Solution**:
- The workflow installs FFmpeg automatically
- If testing locally, install FFmpeg:
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org

### Edge TTS errors

**Solution**:
- Microsoft may have changed their API
- Check https://github.com/rany2/edge-tts/issues for updates
- This is expected for this unofficial library

---

## Testing Locally

Before pushing to GitHub, test locally:

```bash
# Activate virtual environment
source venv/bin/activate  # or: .\venv\Scripts\activate on Windows

# Set environment variables
export CLIENT_SECRETS_CONTENT="$(cat client_secrets.json)"
export YOUTUBE_TOKEN_CONTENT="$(cat token.json)"

# Run the bot
python main.py
```

Check for errors at each stage:
1. ✅ Scraping Reddit
2. ✅ Generating audio
3. ✅ Creating video
4. ✅ Uploading to YouTube

---

## Common Workflow Errors

### "No new posts used. No commit necessary"

This means:
- Reddit scraping failed (403 error)
- All available posts have been used
- No posts met the criteria (all were videos or NSFW)

**Check**: GitHub Actions logs for the exact error message

### Workflow doesn't run automatically

**Solution**:
1. Check the workflow file is in `.github/workflows/bot.yml`
2. Ensure repository is public (required for free GitHub Actions)
3. Check Actions tab → Look for disabled workflows
4. Workflow may be disabled if it failed multiple times

---

## Getting More Help

1. **Check GitHub Actions Logs**:
   - Go to your repo → Actions tab
   - Click on the failed run
   - Expand each step to see detailed output

2. **Test Each Component**:
   ```bash
   # Test Reddit scraping only
   python -c "from reddit_scraper import get_top_reddit_post; print(get_top_reddit_post('AskReddit'))"
   
   # Test TTS
   python -c "import asyncio; import edge_tts; asyncio.run(edge_tts.Communicate('test', 'en-US-JennyNeural').save('test.mp3'))"
   ```

3. **Enable Debug Mode**:
   Add this to the top of `main.py`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## Expected Behavior

When everything works:
1. ✅ GitHub Actions runs every 6 hours
2. ✅ Scrapes a new post from Reddit
3. ✅ Generates audio and video
4. ✅ Uploads to YouTube as "Private"
5. ✅ Commits updated `used_posts.txt`
6. ✅ You see new commit: "AUTOBOT: Update used_posts.txt"
7. ✅ Video appears in YouTube Studio

If you see the AUTOBOT commit and a new video in YouTube Studio, **the system is working perfectly**! 🎉
