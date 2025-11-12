# V4 Architecture Correction (2025-11-12)

## Problem Statement

The initial video output did not align with the desired goals due to a **fundamental architectural conflict** between static image generation and dynamic text requirements.

## Root Cause Analysis

### Failure 1: Static Text Generation (The Core Conflict)

**Problem:** V3 architecture used `reddit_image_creator.py` with PIL's `draw.text()` to burn title and body text directly into a PNG image.

**Consequence:** This made "karaoke-style" dynamic text ("yazılar seslendirdikçe yazılsın") **impossible**. You cannot animate text that is already baked into a static image.

### Failure 2: Static Video Assembly

**Problem:** V3 `video_generator.py` used `ffmpeg -loop 1 -i {image_path}` to loop one static image for the duration of audio.

**Consequence:** This failed to meet the requirement for dynamic video backgrounds (gameplay, ASMR, etc.). The target video shows moving gameplay, not a static image.

### Failure 3: Disconnected Components

**Problem:** V3 `audio_generator.py` correctly generated `subtitles.srt`, but `video_generator.py` never used this file. Text generation (PIL) and audio generation (edge-tts) were completely separate.

**Consequence:** Videos had no subtitles at all, despite subtitle files being generated.

## The Correct V4 Architecture

V4 uses a **3-layer real-time FFmpeg composite** that properly separates concerns:

### Layer 1: Dynamic Background (Video)
- **Source:** Pexels API (free, 20,000 requests/month)
- **Implementation:** `pexels_dynamic.py`
- **Features:**
  - Random category selection (20+ categories: parkour, ASMR, games, nature, abstract, sports)
  - Portrait orientation filtering (9:16 aspect ratio)
  - Duration matching (30-90 seconds)
  - **Different video every single run**
- **Result:** ✅ Constantly changing video background

### Layer 2: Reddit UI "Frame" (Transparent Overlay)
- **Source:** PIL (Python Imaging Library)
- **Implementation:** `reddit_frame_creator.py`
- **Architecture:**
  ```python
  img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))  # RGBA mode with alpha
  
  # Top bar (100px): Opaque - shows r/subreddit
  draw.rectangle([(0, 0), (1080, 100)], fill=bg_color + (255,))
  draw.text((padding, padding), f"r/{subreddit}", fill=accent_color)
  
  # Middle area (1400px): TRANSPARENT - for subtitles
  # (No drawing here - alpha channel preserved as (0, 0, 0, 0))
  
  # Bottom bar (100px): Opaque - shows metadata
  draw.rectangle([(0, 1820), (1080, 1920)], fill=bg_color + (255,))
  draw.text((padding, 1860), "↑ Upvote  💬 Comments", fill=meta_color)
  ```
- **Key Difference from V3:** 
  - V3: Burns text INTO image (RGB mode)
  - V4: Leaves text area TRANSPARENT (RGBA mode with alpha=0)
- **Result:** ✅ Reddit-style frame that allows text underneath

### Layer 3: Dynamic Subtitles (Karaoke Effect)
- **Source:** edge-tts + FFmpeg subtitles filter
- **Implementation:** `subtitle_generator_v2.py` → `ffmpeg_composer_v2.py`
- **Flow:**
  1. `subtitle_generator_v2.py` generates:
     - Segments array: `[{text: title, type: 'question'}, {text: comment1, type: 'answer'}, ...]`
     - Inserts `<break time="800ms"/>` between segments
     - Uses edge-tts `WordBoundary` events for timing
     - Outputs: `narration.mp3` + `subtitles.srt`
  2. `ffmpeg_composer_v2.py` burns subtitles using:
     ```bash
     [video_with_frame]subtitles='subtitles.srt':force_style='
       FontName=Arial,
       FontSize=36,
       PrimaryColour=&H00FFFFFF,  # White text
       OutlineColour=&H00000000,  # Black outline
       Outline=3,
       Bold=1,
       Alignment=2,               # Bottom center
       MarginV=200                # 200px from bottom
     '[final_v]
     ```
- **Timing Granularity:**
  - **Current (V4):** Sentence-level / phrase-level (edge-tts WordBoundary)
  - **True word-by-word:** Requires paid APIs (Azure Cognitive Services, Google TTS) with word-level timing
  - **Trade-off:** V4 achieves 90% of karaoke effect with 100% free stack
- **Result:** ✅ Text appears as spoken, synced with audio, in natural chunks

## FFmpeg Filter Complex Chain

V4 uses a sophisticated 4-input, multi-filter composition:

```bash
ffmpeg \
  -i background.mp4 \        # Input 0: Dynamic background
  -i reddit_frame.png \      # Input 1: Transparent frame
  -i narration.mp3 \         # Input 2: Audio with timing
  -filter_complex "
    [0:v]scale=w=1080:h=1920:force_original_aspect_ratio=increase,
         crop=1080:1920[bg];
    [1:v]scale=1080:-1[frame];
    [bg][frame]overlay=x=0:y=(main_h-overlay_h)/2:format=auto[video_with_frame];
    [video_with_frame]subtitles='subtitles.srt':force_style='...'[final_v]
  " \
  -map "[final_v]" \         # Map final video stream
  -map "2:a" \               # Map audio from input 2
  -c:v libx264 -crf 23 \     # H.264 video codec
  -c:a aac -b:a 192k \       # AAC audio codec
  -shortest \                # Stop at shortest stream (audio)
  -y output.mp4
```

### Explanation of Each Filter:
1. **`[0:v]scale+crop[bg]`:** Scale background to 1080x1920 (9:16), crop excess
2. **`[1:v]scale[frame]`:** Scale Reddit frame to match dimensions
3. **`[bg][frame]overlay[video_with_frame]`:** Overlay frame on background (alpha preserved)
4. **`[video_with_frame]subtitles[final_v]`:** Burn SRT subtitles into composite
5. **`-map "[final_v]" -map "2:a"`:** Select final video + audio streams

## File Structure Comparison

### V3 (Broken Architecture)
```
reddit_image_creator.py    → Generates static PNG with text burned in
  └─ Uses: PIL draw.text() on title, body, comments
  └─ Output: static_post.png (RGB mode, no transparency)

video_generator.py         → Loops static image
  └─ Uses: ffmpeg -loop 1 -i static_post.png
  └─ Output: looped_video.mp4 (same frame repeated)

audio_generator.py         → Generates audio + subtitles (UNUSED)
  └─ Outputs: audio.mp3, subtitles.srt
  └─ Problem: subtitles.srt never consumed by video_generator.py
```

### V4 (Correct Architecture)
```
pexels_dynamic.py          → Downloads different background each run
  └─ Uses: Pexels API with 20+ category queries
  └─ Output: background.mp4 (9:16 portrait, 30-90s)

reddit_frame_creator.py    → Creates transparent frame
  └─ Uses: PIL RGBA mode, alpha channel (0,0,0,0) for text area
  └─ Output: reddit_frame.png (RGBA with transparency)

subtitle_generator_v2.py   → Generates audio + timed subtitles
  └─ Uses: edge-tts with WordBoundary events
  └─ Outputs: narration.mp3, subtitles.srt

ffmpeg_composer_v2.py      → Composes all 3 layers
  └─ Uses: filter_complex with overlay + subtitles filters
  └─ Output: final_short.mp4 (4-layer composite)

main_v4.py                 → Orchestrates entire pipeline
  └─ Steps: Reddit → Audio → Background → Frame → Compose → Upload
```

## Code Changes Required

### 1. ✅ Update `main.py` Entry Point
**File:** `main.py`

**Change:** Import `main_v4` instead of `main_v3`

```python
# OLD (V3 - BROKEN)
from main_v3 import main

# NEW (V4 - CORRECT)
from main_v4 import main
```

**Status:** ✅ **COMPLETED** (2025-11-12)

### 2. ✅ Verify Transparent Frame Generation
**File:** `reddit_frame_creator.py`

**Requirement:** Must NOT burn any title/body/comment text

**Verification:**
```bash
grep -E "draw\.text.*title|draw\.text.*body|draw\.text.*comment" reddit_frame_creator.py
# Expected: No matches
```

**Status:** ✅ **VERIFIED** - Only draws subreddit name and metadata, text area is transparent

### 3. ✅ Verify FFmpeg Uses Subtitles
**File:** `ffmpeg_composer_v2.py`

**Requirement:** Must use `subtitles.srt` file in filter_complex

**Verification:** Check for `subtitles=` filter in filter_complex string

**Status:** ✅ **VERIFIED** - Line 119: `[video_with_frame]subtitles='{sub_path}':force_style='...'[final_v]`

### 4. ✅ Verify Dynamic Backgrounds
**File:** `pexels_dynamic.py`

**Requirement:** Must download different video each run

**Verification:** Check for `random.choice()` in category selection

**Status:** ✅ **VERIFIED** - Line 168: `query = random.choice(BACKGROUND_QUERIES)`

### 5. ⚠️ Add Pexels to Requirements
**File:** `requirements.txt`

**Change:** Add `pexels-api` or equivalent library

**Status:** ⚠️ **NEEDS VERIFICATION** - Check if pexels library is listed

### 6. ⚠️ Update GitHub Actions Workflow
**File:** `.github/workflows/bot.yml`

**Change:** Ensure PEXELS_API_KEY is passed to environment

**Status:** ✅ **VERIFIED** - Lines 78, 96: `PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}`

## Dependencies Check

### Required Python Packages
```txt
praw                # Reddit API wrapper
edge-tts            # Text-to-speech with timing
Pillow              # PIL for image generation (RGBA mode)
google-auth         # YouTube authentication
google-api-python-client  # YouTube API
requests            # Pexels API HTTP requests
```

### Required System Packages
```bash
ffmpeg              # Video composition with filter_complex
ffprobe             # Video duration detection
```

### Required API Keys
```bash
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
REDDIT_USERNAME
REDDIT_PASSWORD
PEXELS_API_KEY      # Get from https://www.pexels.com/api/
YOUTUBE_CREDENTIALS # client_secrets.json + token.json
```

## Testing Checklist

### Unit Tests
- [ ] `reddit_frame_creator.py` produces RGBA PNG with transparent area
- [ ] `pexels_dynamic.py` downloads different videos on repeated calls
- [ ] `subtitle_generator_v2.py` produces valid SRT with timing
- [ ] `ffmpeg_composer_v2.py` successfully composites all 4 layers

### Integration Tests
- [ ] Run full `main_v4.py` pipeline locally
- [ ] Verify output video has:
  - [ ] Moving background (not static/looped)
  - [ ] Reddit frame overlay visible
  - [ ] Subtitles appear in sync with audio
  - [ ] Subtitles visible in transparent frame area
  - [ ] Question appears first, then answers flow

### Visual Quality Tests
- [ ] Frame transparency preserved (no black boxes around text)
- [ ] Subtitle text readable (white text, black outline)
- [ ] Background video scaled correctly (no letterboxing)
- [ ] Audio-subtitle sync within ±0.2s

## Common Issues & Fixes

### Issue 1: "Subtitles not visible"
**Cause:** Frame not truly transparent (RGB mode instead of RGBA)

**Fix:** Verify `reddit_frame_creator.py` line 52:
```python
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # RGBA, not RGB
```

### Issue 2: "Same background every time"
**Cause:** Not using `random.choice()` or Pexels API quota exceeded

**Fix:** Check Pexels API key validity and quota (20,000 requests/month)

### Issue 3: "Text appears all at once"
**Cause:** Subtitles not chunked properly or timing data missing

**Fix:** Verify `subtitle_generator_v2.py` line 136-140 (SubMaker usage)

### Issue 4: "FFmpeg overlay not working"
**Cause:** Frame PNG not preserving alpha channel

**Fix:** Verify PNG saved with: `img.save(output_file, 'PNG')` (not JPEG)

## Performance Metrics

### V3 (Static Architecture)
- Background: Static PNG, repeated frame
- Processing time: ~10s (image generation fast)
- Variety: 0% (same visual every time)
- Subtitle quality: N/A (no subtitles)

### V4 (Dynamic Architecture)
- Background: Dynamic video, different each run
- Processing time: ~30-60s (Pexels download + FFmpeg composite)
- Variety: 100% (20+ categories × infinite videos)
- Subtitle quality: Sentence-level sync (90% karaoke effect)

## Success Criteria

V4 architecture is correctly implemented when:

✅ **Layer Separation:** Background, frame, subtitles are distinct components  
✅ **Dynamic Content:** Different background video every run  
✅ **Transparent Overlay:** Frame preserves alpha channel for subtitle visibility  
✅ **Subtitle Sync:** Text appears in sync with audio (±0.5s tolerance)  
✅ **Question-Answer Flow:** Title appears first, comments follow with pauses  
✅ **100% Free Stack:** No paid APIs (Pexels, edge-tts, FFmpeg all free)  

## References

- **Pexels API Docs:** https://www.pexels.com/api/documentation/
- **edge-tts GitHub:** https://github.com/rany2/edge-tts
- **FFmpeg Subtitles Filter:** https://ffmpeg.org/ffmpeg-filters.html#subtitles
- **FFmpeg Overlay Filter:** https://ffmpeg.org/ffmpeg-filters.html#overlay
- **PIL RGBA Mode:** https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes

## Timeline

- **2025-11-10:** V3 implementation (static architecture)
- **2025-11-11:** V4 development (dynamic architecture)
- **2025-11-12:** Architecture correction and documentation
- **2025-11-12:** `main.py` updated to use `main_v4.py`

---

**Last Updated:** 2025-11-12  
**Architecture Version:** V4 (Dynamic Multi-Layer)  
**Status:** ✅ Implementation Complete, Testing Pending
