#!/usr/bin/env python3
"""
main_v4.py
V4 Gelişmiş Orkestrasyon - Tam Yeni Mimari
Reddit → YouTube Shorts (Tam Otomatik)

Özellikler:
1. Dinamik arka plan (Pexels API - her seferinde farklı)
2. Reddit çerçevesi (PIL - şeffaf metin alanı)
3. Karaoke altyazılar (edge-tts - cümle düzeyinde)
4. Soru > Cevap akışı (başlık sonra yorumlar)
"""

import os
import sys
from reddit_fetcher import authenticate_reddit, fetch_popular_post
from reddit_frame_creator import create_frame_for_post
from pexels_dynamic import get_background_for_duration
from subtitle_generator_v2 import generate_audio_with_flow_sync, VOICE_PRESETS_V2
from subtitle_generator_v3 import generate_audio_with_flow_gtts  # Fallback
from ffmpeg_composer_v2 import compose_video_v2
import youtube_uploader

# --- V4 Configuration ---
SUBREDDIT = "AskReddit"
VIDEO_TITLE_PREFIX = "Reddit Asks: "
VOICE = VOICE_PRESETS_V2["male_us"]  # Varsayılan ses
AUDIO_RATE = "+10%"  # 1.1x hız
MAX_COMMENTS = 5  # Maksimum yorum sayısı

# SEO-optimized tags and hashtags
VIDEO_TAGS = [
    "reddit", "askreddit", "reddit stories", "reddit story time",
    "ask reddit", "shorts", "youtube shorts",
    "viral", "storytelling", "reddit asks", "reddit thread",
    "reddit compilation", "trending", "reddit questions"
]

VIDEO_HASHTAGS = [
    "#redditstories",
    "#askreddit", 
    "#shorts",
    "#viral",
    "#trending",
    "#reddit"
]
# ---------------------


def main():
    print("=" * 70)
    print("🤖 Reddit-to-YouTube Shorts Bot V4 (Advanced Architecture)")
    print("=" * 70)
    print()
    
    try:
        # -------------------------------------------------------------------------
        # STEP 1: Reddit Post Fetching
        # -------------------------------------------------------------------------
        print("📋 Step 1/6: Fetching Reddit post...")
        
        reddit = authenticate_reddit()
        if not reddit:
            print("❌ Reddit authentication failed")
            sys.exit(1)
        
        post_data = fetch_popular_post(reddit, SUBREDDIT)
        if not post_data:
            print("❌ No suitable Reddit post found")
            sys.exit(1)
        
        title = post_data['title']
        url = post_data['url']
        post_id = post_data['id']
        comments = post_data.get('comments', [])[:MAX_COMMENTS]
        
        print()
        print("✅ Post selected:")
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        print(f"   Comments: {len(comments)}")
        print()
        
        # -------------------------------------------------------------------------
        # STEP 2: Generate Audio + Subtitles (Question > Answer Flow)
        # -------------------------------------------------------------------------
        print("📋 Step 2/6: Generating audio with flow-based subtitles...")
        print("   Flow: Question first → Answers with pauses")
        
        # Try edge-tts first, fallback to gTTS if it fails
        result = generate_audio_with_flow_sync(
            title=title,
            comments=comments,
            audio_file="narration.mp3",
            subtitle_file="subtitles.srt",
            voice=VOICE,
            rate=AUDIO_RATE,
            pause_between=0.8  # Soru-cevap arası 0.8s duraklama
        )
        
        if not result:
            print("⚠️  edge-tts failed, trying fallback gTTS...")
            result = generate_audio_with_flow_gtts(
                title=title,
                comments=comments,
                audio_file="narration.mp3",
                subtitle_file="subtitles.srt",
                lang="en",
                pause_between=1.0
            )
        
        if not result:
            print("❌ Failed to generate audio/subtitles with both methods")
            sys.exit(1)
        
        audio_file, subtitle_file = result
        print(f"✅ Audio ready: {audio_file}")
        print(f"✅ Subtitles ready: {subtitle_file}")
        print()
        
        # Ses süresini al (arka plan için)
        from ffmpeg_composer_v2 import get_video_duration
        audio_duration = get_video_duration(audio_file)
        if audio_duration:
            print(f"   Audio duration: {audio_duration:.1f}s")
        else:
            audio_duration = 60  # Varsayılan
        
        # -------------------------------------------------------------------------
        # STEP 3: Dynamic Background Video (Different Every Time!)
        # -------------------------------------------------------------------------
        print()
        print("📋 Step 3/6: Downloading dynamic background video...")
        print("   🔄 Each run gets a DIFFERENT video!")
        
        background_video = get_background_for_duration(
            target_duration=audio_duration,
            output_file="background.mp4"
        )
        
        if not background_video:
            print("❌ Failed to download background video")
            sys.exit(1)
        
        print(f"✅ Background ready: {background_video}")
        print()
        
        # -------------------------------------------------------------------------
        # STEP 4: Create Reddit Frame (With Transparent Text Area)
        # -------------------------------------------------------------------------
        print("📋 Step 4/6: Creating Reddit frame...")
        print("   Frame has TRANSPARENT area for subtitles")
        
        reddit_frame = create_frame_for_post(
            post_data=post_data,
            output_file="reddit_frame.png"
        )
        
        if not reddit_frame:
            print("❌ Failed to create Reddit frame")
            sys.exit(1)
        
        print(f"✅ Frame ready: {reddit_frame}")
        print()
        
        # -------------------------------------------------------------------------
        # STEP 5: Compose Final Video (4-Layer Architecture)
        # -------------------------------------------------------------------------
        print("📋 Step 5/6: Composing final video...")
        print("   Architecture:")
        print("   Layer 1: Background video (dynamic)")
        print("   Layer 2: Reddit frame (transparent text area)")
        print("   Layer 3: Burned subtitles (karaoke style)")
        print("   Layer 4: Audio track (synced)")
        print()
        
        final_video = compose_video_v2(
            background_video=background_video,
            reddit_frame=reddit_frame,
            subtitle_file=subtitle_file,
            audio_file=audio_file,
            output_file="final_short.mp4",
            subtitle_style={
                'font': 'Arial',
                'font_size': 36,
                'primary_color': '&H00FFFFFF',  # White
                'outline_color': '&H00000000',  # Black outline
                'outline': 3,
                'shadow': 2,
                'bold': 1,
                'alignment': 2,  # Bottom center
                'margin_v': 200  # 200px from bottom
            }
        )
        
        if not final_video:
            print("❌ Failed to compose final video")
            sys.exit(1)
        
        print(f"✅ Final video ready: {final_video}")
        print()
        
        # -------------------------------------------------------------------------
        # STEP 6: Upload to YouTube
        # -------------------------------------------------------------------------
        print("📋 Step 6/6: Uploading to YouTube...")
        
        # Build metadata
        video_title = f"{VIDEO_TITLE_PREFIX}{title[:80]}"  # 100 char limit
        
        # Description with hashtags
        video_description = (
            f"{title}\n\n"
            f"From r/{SUBREDDIT}\n\n"
            f"Top comments:\n"
        )
        
        for i, comment in enumerate(comments[:3], 1):
            author = comment.get('author', 'unknown')
            body = comment.get('body', '')[:100]
            video_description += f"{i}. u/{author}: {body}...\n"
        
        video_description += "\n" + " ".join(VIDEO_HASHTAGS)
        
        # Authenticate YouTube
        youtube_service = youtube_uploader.get_authenticated_service()
        if not youtube_service:
            print("❌ YouTube authentication failed")
            sys.exit(1)
        
        # Upload
        upload_result = youtube_uploader.upload_video(
            youtube_service=youtube_service,
            file_path=final_video,
            title=video_title,
            description=video_description,
            tags=VIDEO_TAGS
        )
        
        if upload_result == "quota_exceeded":
            print()
            print("⚠️  YouTube quota exceeded!")
            print("   Video saved for manual upload:")
            print(f"   {final_video}")
            
            # Save for manual upload
            youtube_uploader.save_video_for_manual_upload(
                video_path=final_video,
                title=video_title,
                description=video_description,
                tags=VIDEO_TAGS,
                post_id=post_id
            )
            
            # Mark post as used anyway
            from reddit_scraper import mark_post_as_used
            mark_post_as_used(post_id)
            
        elif upload_result:
            print()
            print("🎉 SUCCESS! Video uploaded to YouTube!")
            print(f"   Title: {video_title}")
            print(f"   Post ID: {post_id}")
            
            # Mark post as used
            from reddit_fetcher import mark_post_as_used
            mark_post_as_used(post_id)
            
        else:
            print("❌ Upload failed")
            sys.exit(1)
        
        print()
        print("=" * 70)
        print("✅ Bot completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Bot interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
