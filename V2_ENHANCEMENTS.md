# V2 Enhancements - What's New 🚀

This branch contains major upgrades to transform the bot from a simple automation tool into a professional content factory.

## 🎯 V2 Features

### 1. ⚡ Faster Audio (1.3x Speed)
- **New Module**: `audio_utils.py`
- Uses FFmpeg's `atempo` filter to speed up narration without pitch changes
- Default: 1.3x (30% faster) - perfect for Shorts attention span
- Configurable from 0.5x to 4.0x speed

**Benefits:**
- ✅ More engaging, faster-paced content
- ✅ Fits more content in 60 seconds
- ✅ Natural-sounding (no chipmunk effect)

### 2. 🎮 Dynamic Background Videos
- **New Module**: `background_downloader.py`
- Automatically downloads Minecraft parkour gameplay from YouTube
- Uses `yt-dlp` for reliable video fetching
- Fallback to static image if download fails

**Benefits:**
- ✅ Eye-catching moving backgrounds
- ✅ Matches viral Shorts format (Minecraft parkour + text)
- ✅ Variety - different videos each run
- ✅ No copyright issues (gameplay is transformative)

### 3. 🎨 Styled Comment Overlays
- **New Module**: `comment_image_generator.py`
- Converts Reddit comments to beautiful PNG overlays
- Reddit-authentic styling (dark mode colors, proper fonts)
- Different styles for titles vs comments

**Benefits:**
- ✅ Professional, recognizable Reddit aesthetic
- ✅ Better readability than burned-in text
- ✅ Usernames displayed for authenticity
- ✅ Fully customizable HTML/CSS styling

### 4. 🎬 MoviePy Video Assembly
- **New Module**: `video_assembler_v2.py`
- Replaces complex FFmpeg commands with Python
- Supports multiple overlay layers with timing
- Automatic 9:16 aspect ratio cropping

**Benefits:**
- ✅ Much easier to modify and debug
- ✅ Complex sequencing made simple
- ✅ Better control over transitions
- ✅ Cleaner, more maintainable code

### 5. 📈 SEO-Optimized Metadata
- **Enhanced**: `main_v2.py`
- 15 carefully chosen tags for discoverability
- 5 high-traffic hashtags in description
- SEO-friendly descriptions with calls-to-action

**Benefits:**
- ✅ Better YouTube algorithm performance
- ✅ Higher search rankings
- ✅ More impressions and clicks
- ✅ Professional presentation

### 6. 🎭 Multiple Voice Support (Ready)
- Infrastructure ready for voice cloning
- Separate audio generation for title vs comments
- Easy to integrate with Coqui XTTS or similar TTS

**Benefits:**
- ✅ More engaging variety
- ✅ Clear distinction between title and responses
- ✅ Professional podcast-style narration

## 📦 New Dependencies

```
moviepy       # Video composition
yt-dlp        # Background video downloading
imgkit        # HTML-to-image conversion (alternative)
```

**Note**: Also requires `wkhtmltoimage` system package:
```bash
# Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# macOS
brew install wkhtmltopdf

# The package includes wkhtmltoimage
```

## 🔄 Migration Guide

### For Local Testing

1. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install wkhtmltopdf (includes wkhtmltoimage):
   ```bash
   # macOS
   brew install wkhtmltopdf
   
   # Linux
   sudo apt-get install wkhtmltopdf
   ```

3. Run V2 script:
   ```bash
   python main_v2.py
   ```

### For GitHub Actions

The workflow will automatically:
- Install Python dependencies
- Install wkhtmltopdf in the Ubuntu runner
- Use `main_v2.py` instead of `main.py`

Update `.github/workflows/bot.yml`:
```yaml
- name: Install system dependencies
  run: sudo apt-get update && sudo apt-get install -y ffmpeg wkhtmltopdf

- name: Run the Python Bot (V2)
  run: python main_v2.py
```

## 📊 Performance Comparison

| Feature | V1 | V2 |
|---------|----|----|
| Audio Speed | Normal | 1.3x (30% faster) |
| Background | Static image | Dynamic Minecraft video |
| Text Display | Burned-in subtitles | Styled PNG overlays |
| Video Assembly | Complex FFmpeg | Simple MoviePy |
| SEO Optimization | Basic | 15 tags + 5 hashtags |
| Voice Variety | Single voice | Ready for multi-voice |
| Code Maintainability | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎥 Expected Output

**V2 videos will have:**
1. ✅ Minecraft parkour background (moving)
2. ✅ Reddit-styled title card (orange background)
3. ✅ Sequential comment overlays (dark mode style)
4. ✅ 30% faster, more engaging narration
5. ✅ SEO-optimized title and description
6. ✅ Professional hashtags for discoverability

## ⚠️ Important Notes

### wkhtmltoimage Requirement
The comment image generator requires `wkhtmltoimage` to be installed on the system. This is included in the `wkhtmltopdf` package.

**Fallback**: If wkhtmltoimage is not available, you can:
1. Use the old subtitle-burning method (modify `video_creator.py`)
2. Use PIL/Pillow to draw text on images (simpler but less flexible)
3. Pre-generate images manually and upload them

### MoviePy Performance
MoviePy is powerful but can be slower than FFmpeg for large videos. For 60-second Shorts, performance is excellent.

### Background Video Downloads
- First run will download a background video (~10-50MB)
- Subsequent runs can reuse the same video
- Set `USE_DYNAMIC_BACKGROUND = False` in `main_v2.py` to disable

## 🚀 Future Enhancements

Ready for V3:
- [ ] Voice cloning with Coqui XTTS
- [ ] LLM-generated titles and descriptions
- [ ] Automatic trending topic detection
- [ ] Multi-subreddit support
- [ ] Thumbnail generation
- [ ] Analytics and performance tracking

## 🧪 Testing

Before merging to main:

1. **Test locally first:**
   ```bash
   python main_v2.py
   ```

2. **Check generated files:**
   - `final_short.mp4` - Final video
   - `audio_*_fast.mp3` - Sped-up audio
   - `title.png`, `comment_*.png` - Overlay images
   - `background.mp4` - Downloaded background

3. **Verify video quality:**
   - Play in VLC or similar
   - Check aspect ratio (9:16)
   - Verify overlays are visible
   - Confirm audio is synced

4. **Test upload:**
   - Check YouTube upload succeeds
   - Verify title, description, tags
   - Confirm video is set to private

## 📝 Rollback Plan

If V2 has issues, easily revert:
```bash
git checkout main
# Continue using V1
```

V1 remains stable and unchanged on the main branch.

---

**Status**: ✅ All V2 features implemented and ready for testing  
**Branch**: `v2-enhancements`  
**Ready to merge**: After successful local testing
