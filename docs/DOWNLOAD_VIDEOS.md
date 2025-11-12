# How to Download Pending Videos from GitHub Actions

## The Problem
When the bot runs in GitHub Actions and hits the quota limit:
- Videos are saved to `pending_uploads/` **on the remote server**
- The server deletes everything after the workflow finishes
- You can't access them directly

## The Solution: GitHub Artifacts

I've updated the workflow to automatically upload pending videos as **GitHub Artifacts**. These are downloadable files stored by GitHub for 30 days.

---

## How to Download Your Videos

### Step 1: Go to Actions Tab
Visit: https://github.com/demirbase/youtube-shorts-bot/actions

### Step 2: Find the Workflow Run
- Look for the most recent workflow run (should be at the top)
- Click on it to see the details

### Step 3: Download Artifacts
- Scroll down to the **Artifacts** section (below the workflow steps)
- You'll see: `pending-videos-{run_number}` (e.g., `pending-videos-123`)
- Click on it to download a ZIP file

### Step 4: Extract and Upload
- Unzip the downloaded file
- Inside you'll find:
  - `{timestamp}_{postid}_{title}.mp4` - The video file
  - `{timestamp}_{postid}_metadata.json` - Title, description, tags
- Upload manually to YouTube using the metadata

---

## Example Workflow Run with Artifacts

```
Workflow Run #123 (Nov 11, 2025)
├── ✅ Step 1: Check out repository
├── ✅ Step 2: Set up Python
├── ✅ Step 3: Set up FFmpeg
├── ✅ Step 4: Install dependencies
├── ✅ Step 5: Install Python packages
├── ✅ Step 6: Install Playwright
├── ✅ Step 7: Load secrets
├── ⚠️  Step 8: Run the Python Bot (quota exceeded)
├── ✅ Step 9: Upload pending videos
└── ✅ Step 10: Commit state file

Artifacts (expires in 30 days):
📦 pending-videos-123
   └── pending_uploads/
       ├── 20251111_143022_1otf7g7_Americans_if_Bernie_Sanders.mp4
       └── 20251111_143022_1otf7g7_metadata.json
```

---

## What Gets Uploaded

**Only when quota is exceeded:**
- All files in `pending_uploads/` folder
- Both `.mp4` video files and `.json` metadata files
- Stored for 30 days
- Named with workflow run number for easy tracking

**If no quota issues:**
- No artifacts uploaded (video uploaded to YouTube successfully)

---

## Artifact Retention

- **Duration:** 30 days
- **Size limit:** 10 GB per artifact (plenty for videos)
- **Auto-cleanup:** GitHub deletes after 30 days
- **Manual delete:** You can delete artifacts early if needed

---

## Check Previous Runs

If you already ran the bot and hit quota:

1. Go to: https://github.com/demirbase/youtube-shorts-bot/actions
2. Find the run that failed with "quota exceeded"
3. **If it was BEFORE this update:** No artifacts (videos are lost)
4. **If it's AFTER this update:** Artifacts will be available

---

## Troubleshooting

### "No artifacts" on old runs
- Artifacts only work for runs **after** this update
- Previous quota-exceeded runs don't have artifacts
- Videos from those runs are gone (ephemeral server storage)

### Download ZIP is empty
- Check if bot actually hit quota exceeded
- Look at Step 8 logs: should show "Video saved for manual upload"
- If it says "Upload failed" (not quota), no pending videos created

### Artifact expired
- After 30 days, GitHub auto-deletes artifacts
- Need to re-run the bot to regenerate video
- Consider uploading videos sooner

---

## Future Enhancement Ideas

### Option A: Commit to Repo Branch
Instead of artifacts, commit videos to a `pending-uploads` branch:
- Pros: Permanent storage, easy access
- Cons: Large files in Git, quota limits

### Option B: Upload to Cloud Storage
Upload to S3, Google Drive, or Dropbox:
- Pros: Automated, no manual download
- Cons: Requires additional credentials/setup

### Option C: Email Videos
Send videos as email attachments:
- Pros: Delivered directly to you
- Cons: Size limits, spam filters

---

**Created:** 2025-11-11  
**Updated workflow:** commit e29757f  
**Works with:** v3-quota-handling branch and newer
