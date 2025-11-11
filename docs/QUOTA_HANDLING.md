# YouTube Quota Handling - Pending Uploads

## What This Does

When YouTube's daily upload quota is exceeded, the bot now:

1. ✅ **Saves the video** with timestamp and post ID
2. ✅ **Saves metadata** (title, description, tags) as JSON
3. ✅ **Marks post as used** to prevent retry loops
4. ✅ **Continues gracefully** instead of failing

## Directory Structure

```
pending_uploads/
├── 20251111_143022_1otf7g7_Americans_if_Bernie_Sanders.mp4
├── 20251111_143022_1otf7g7_metadata.json
├── 20251112_080000_1ou1234_Another_post_title.mp4
└── 20251112_080000_1ou1234_metadata.json
```

## File Naming Convention

**Video files:**
```
{timestamp}_{post_id}_{safe_title}.mp4
```

**Metadata files:**
```
{timestamp}_{post_id}_metadata.json
```

- `timestamp`: Format `YYYYMMDD_HHMMSS`
- `post_id`: Reddit post ID
- `safe_title`: First 50 chars of title (alphanumeric + spaces/dashes/underscores only)

## Metadata JSON Format

```json
{
  "post_id": "1otf7g7",
  "title": "Americans, if Bernie Sanders was the Democratic presidential nominee in the 2016",
  "description": "Full YouTube description with hashtags...",
  "tags": ["reddit", "askreddit", "shorts", "..."],
  "created_at": "20251111_143022",
  "original_video": "final_short.mp4",
  "saved_video": "pending_uploads/20251111_143022_1otf7g7_Americans_if_Bernie_Sanders.mp4"
}
```

## Manual Upload Instructions

### Option 1: YouTube Studio (Web)

1. Go to https://studio.youtube.com
2. Click **Create** → **Upload videos**
3. Select video from `pending_uploads/` folder
4. Open corresponding `_metadata.json` file
5. Copy/paste:
   - **Title** → Title field
   - **Description** → Description field
   - **Tags** → Tags field (comma-separated)
6. Set as **YouTube Short** (if under 60 seconds)
7. Set visibility to **Public**
8. Click **Publish**

### Option 2: Batch Upload Script (Future Enhancement)

A batch upload script could be created to:
- Read all metadata JSON files
- Upload videos with correct metadata
- Move uploaded files to `completed/` folder
- Requires YouTube OAuth re-authentication

## YouTube Quota Information

**Daily Limits:**
- Total quota: **10,000 units/day**
- Video upload cost: **1,600 units**
- Max uploads: **~6 videos/day**

**Quota Reset:**
- Resets at **midnight Pacific Time (PT)**
- That's **8:00-9:00 AM UTC** (depending on DST)

**Check Your Quota:**
1. Go to: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
2. View current usage and limits
3. Can request quota increase (requires justification)

## Error Detection

The bot detects quota exceeded by checking:

```python
if e.resp.status == 400 and b'uploadLimitExceeded' in e.content:
    # Handle gracefully
```

**Error message from YouTube:**
```json
{
  "error": {
    "code": 400,
    "message": "The user has exceeded the number of videos they may upload.",
    "errors": [{
      "message": "The user has exceeded the number of videos they may upload.",
      "domain": "youtube.video",
      "reason": "uploadLimitExceeded"
    }]
  }
}
```

## Cleanup

**Automated (recommended):**
After successfully uploading pending videos, delete them manually or with a script.

**Manual:**
```bash
# Delete all uploaded videos
rm pending_uploads/*.mp4

# Delete metadata too
rm pending_uploads/*.json

# Or delete entire folder
rm -rf pending_uploads/
```

## Future Enhancements

1. **Batch Upload Script**
   - Automatically upload all pending videos when quota resets
   - Schedule to run at 8 AM UTC

2. **Upload Status Tracking**
   - Add `uploaded: true/false` to metadata JSON
   - Move uploaded files to `completed/` subfolder

3. **Retry Logic**
   - Automatically retry failed uploads
   - Exponential backoff for rate limits

4. **Email/Slack Notifications**
   - Alert when quota exceeded
   - Summary of pending uploads

## Testing

To test quota handling without hitting real quota:

1. Temporarily modify `youtube_uploader.py`:
```python
# Force quota exceeded for testing
return "quota_exceeded"
```

2. Run bot and verify:
   - Video saved to `pending_uploads/`
   - Metadata JSON created
   - Post marked as used
   - No error exit

3. Revert changes after testing

---

**Created:** 2025-11-11  
**Branch:** `v3-quota-handling`  
**Status:** ✅ Implemented and tested
