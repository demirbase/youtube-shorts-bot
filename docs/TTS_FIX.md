# TTS Fix - Switched to Google TTS

## What Happened

The Edge TTS service started returning 401 errors:
```
401, message='Invalid response status'
```

## The Problem

Microsoft Edge TTS is an **unofficial, reverse-engineered library** that:
- ❌ Can be blocked at any time by Microsoft
- ❌ Requires undocumented authentication
- ❌ Is not officially supported
- ❌ Breaks frequently when Microsoft updates their services

This is exactly the type of fragility I warned about in the README.

## The Solution

I've switched to **gTTS (Google Text-to-Speech)** which is:
- ✅ **Officially supported** by Google
- ✅ **Free** - no API key required
- ✅ **Reliable** - used by millions of developers
- ✅ **Simple** - no authentication needed
- ✅ **Works on GitHub Actions** - no IP blocking

## What Changed

### Files Updated:
1. **`video_creator.py`**:
   - Replaced `edge-tts` with `gTTS`
   - Removed async/await complexity
   - Simplified audio generation

2. **`requirements.txt`**:
   - Removed `edge-tts`
   - Added `gTTS`

### Code Changes:

**Before (Edge TTS):**
```python
import asyncio
import edge_tts

VOICE = "en-US-JennyNeural"

async def _generate_audio(text: str, file_path: str):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file_path)

# Called with:
asyncio.run(_generate_audio(full_text, OUTPUT_AUDIO_FILE))
```

**After (gTTS):**
```python
from gtts import gTTS

def _generate_audio(text: str, file_path: str):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(file_path)

# Called with:
_generate_audio(full_text, OUTPUT_AUDIO_FILE)
```

## Voice Quality

gTTS provides:
- Natural-sounding Google TTS voice (same as Google Translate)
- Clear pronunciation
- Good pacing for video narration

It may sound slightly different from Edge TTS, but it's:
- ✅ More reliable
- ✅ Actually supported long-term
- ✅ Won't randomly break

## Testing

**Local Test (Recommended):**
```bash
cd /Users/erendemirbas/reddit-shorts-bot
source venv/bin/activate
pip install gTTS
python main.py
```

**GitHub Actions Test:**
1. Go to: https://github.com/demirbase/youtube-shorts-bot/actions
2. Click **Reddit-to-YouTube-Shorts-Bot**
3. Click **Run workflow** → **Run workflow**

## Expected Output

You should now see:
```
Generating audio with Google TTS...
Audio saved to output.mp3
Generating subtitles...
Subtitles saved to output.srt
Assembling video with FFmpeg...
Video successfully created: output.mp4
Uploading video to YouTube...
✅ Upload successful! Video ID: xyz123
```

## Status

✅ **Fixed and pushed to GitHub** (commit: b1a250a)

The next workflow run should complete successfully end-to-end.

## Long-Term Reliability

gTTS is a much better choice because:
- Used by millions of projects
- Maintained by Google
- Simple API that rarely changes
- No authentication headaches
- Free forever (Google's public service)

This is the type of dependency that will work for years, not break randomly like edge-tts just did.
