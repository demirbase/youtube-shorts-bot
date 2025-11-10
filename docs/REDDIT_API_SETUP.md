# Reddit API Setup Guide

## Why This Is Needed

Reddit blocks GitHub Actions IP addresses with 403 errors. The solution is to use **Reddit's Official API** which:
- ✅ Never gets blocked
- ✅ Has 30x higher rate limits (600 requests per 10 minutes)
- ✅ Is officially supported and stable
- ✅ Requires authentication (but that's a good thing)

## Step-by-Step Setup

### Step 1: Create a Reddit App

1. **Log in to Reddit** with the account you want to use
2. Go to: https://www.reddit.com/prefs/apps
3. Scroll to the bottom and click **"create another app..."**
4. Fill in the form:
   - **name**: `reddit-shorts-bot` (or any name you want)
   - **App type**: Select **"script"**
   - **description**: Optional, e.g., "Automated content bot"
   - **about url**: Leave blank or use your GitHub repo URL
   - **redirect uri**: `http://localhost:8080`
5. Click **"create app"**

### Step 2: Get Your Credentials

After creating the app, you'll see:
- **client_id**: A string under the app name (looks like: `abc123XYZ456`)
- **secret**: The "secret" field (looks like: `deFgHiJkLmNoPqRsTuVwXyZ123456`)

**Save these!** You'll need them in the next step.

### Step 3: Add Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add each of these:

**Secret 1: REDDIT_CLIENT_ID**
- Name: `REDDIT_CLIENT_ID`
- Value: The client_id from Step 2 (the short string under your app name)

**Secret 2: REDDIT_CLIENT_SECRET**
- Name: `REDDIT_CLIENT_SECRET`  
- Value: The "secret" value from Step 2

**Secret 3: REDDIT_USERNAME**
- Name: `REDDIT_USERNAME`
- Value: Your Reddit username (without the /u/)

**Secret 4: REDDIT_PASSWORD**
- Name: `REDDIT_PASSWORD`
- Value: Your Reddit account password

⚠️ **Security Note**: These credentials give access to your Reddit account. Use a dedicated Reddit account for the bot if possible.

### Step 4: Update the Workflow

The workflow file needs to pass these new secrets. Edit `.github/workflows/bot.yml`:

Find this section:
```yaml
- name: 5. Load Secrets into Environment
  env:
    CLIENT_SECRETS: ${{ secrets.CLIENT_SECRETS }}
    YOUTUBE_TOKEN: ${{ secrets.YOUTUBE_TOKEN }}
  run: |
    echo "CLIENT_SECRETS_CONTENT=$CLIENT_SECRETS" >> $GITHUB_ENV
    echo "YOUTUBE_TOKEN_CONTENT=$YOUTUBE_TOKEN" >> $GITHUB_ENV
```

**Replace it with**:
```yaml
- name: 5. Load Secrets into Environment
  env:
    CLIENT_SECRETS: ${{ secrets.CLIENT_SECRETS }}
    YOUTUBE_TOKEN: ${{ secrets.YOUTUBE_TOKEN }}
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
    REDDIT_USERNAME: ${{ secrets.REDDIT_USERNAME }}
    REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
  run: |
    echo "CLIENT_SECRETS_CONTENT=$CLIENT_SECRETS" >> $GITHUB_ENV
    echo "YOUTUBE_TOKEN_CONTENT=$YOUTUBE_TOKEN" >> $GITHUB_ENV
    echo "REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID" >> $GITHUB_ENV
    echo "REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET" >> $GITHUB_ENV
    echo "REDDIT_USERNAME=$REDDIT_USERNAME" >> $GITHUB_ENV
    echo "REDDIT_PASSWORD=$REDDIT_PASSWORD" >> $GITHUB_ENV
```

### Step 5: Test Locally (Optional but Recommended)

Before pushing to GitHub, test locally:

```bash
# Activate your virtual environment
source venv/bin/activate  # or: .\venv\Scripts\activate on Windows

# Install the new dependency
pip install praw

# Set environment variables (replace with your actual values)
export REDDIT_CLIENT_ID="your_client_id_here"
export REDDIT_CLIENT_SECRET="your_secret_here"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
export CLIENT_SECRETS_CONTENT="$(cat client_secrets.json)"
export YOUTUBE_TOKEN_CONTENT="$(cat token.json)"

# Run the bot
python main.py
```

If it works locally, push to GitHub!

### Step 6: Commit and Push

```bash
git add .
git commit -m "Switch to Reddit's official API (PRAW) for reliability"
git push
```

### Step 7: Run the Workflow

1. Go to your GitHub repo → **Actions** tab
2. Click **Reddit-to-YouTube-Shorts-Bot**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs

You should now see:
```
✅ Found new eligible post: [post_id]
✅ Successfully fetched post with 3 comments
```

## Benefits of This Approach

| Feature | Old Method (.json) | New Method (PRAW) |
|---------|-------------------|-------------------|
| Reliability | ❌ Blocked by GitHub Actions | ✅ Always works |
| Rate Limit | ~20 requests/hour | ✅ 600 requests/10 min |
| Authentication | ❌ None (suspicious) | ✅ Official OAuth |
| Support | ❌ Unofficial, can break | ✅ Official library |
| Setup Complexity | ✅ None | ⚠️ Requires Reddit app |

## Troubleshooting

### "Invalid credentials" error
- Double-check your `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
- Make sure there are no extra spaces
- Verify the secrets are named exactly as shown above

### "Incorrect username or password"
- Verify `REDDIT_USERNAME` is correct (no /u/ prefix)
- Check `REDDIT_PASSWORD` is correct
- Try logging in to reddit.com manually to verify

### "praw module not found"
- Make sure `praw` is in `requirements.txt`
- The workflow installs it automatically
- If testing locally: `pip install praw`

## Alternative: Create a Dedicated Bot Account

For better security, create a new Reddit account specifically for the bot:

1. Create new Reddit account (e.g., `your-bot-username`)
2. Create the Reddit app using this account
3. Use this account's credentials in GitHub Secrets

This way, if something goes wrong, your main Reddit account isn't affected.

---

**That's it!** Once configured, your bot will work reliably without any IP blocking issues. 🎉
