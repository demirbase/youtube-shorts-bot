# main.py
# Main orchestration script - V4 ADVANCED ARCHITECTURE
# 
# ARCHITECTURE CORRECTION (2025-11-12):
# The previous V3 implementation had a fundamental flaw:
# - It burned text into a static PNG using PIL (reddit_image_creator.py)
# - It looped that static image over audio (video_generator.py)
# - This made "karaoke-style" dynamic text IMPOSSIBLE
#
# NEW V4 ARCHITECTURE (Multi-Layer Composite):
# 1. Dynamic background video (Pexels API - different every time)
# 2. Reddit UI frame (PIL with TRANSPARENT text area)
# 3. Dynamic subtitles (burned by FFmpeg, synced with audio)
# 4. Audio track (edge-tts with timing data)
#
# This correctly implements:
# ✅ Dynamic video backgrounds (not static looped images)
# ✅ Karaoke-style text (subtitles appear as spoken)
# ✅ Question → Answer flow (title first, then comments)
# ✅ Reddit-style appearance (frame overlay)

from main_v4 import main

# Run the V4 bot
if __name__ == "__main__":
    main()
