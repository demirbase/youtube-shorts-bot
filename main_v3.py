# main_v3.py
# V3 orchestration following Turkish specification:
# Pexels API → Playwright screenshot → edge-tts with subtitles → FFmpeg filter_complex

import os
import sys
import reddit_scraper
import youtube_uploader
from pexels_downloader import download_pexels_video, get_random_query
from reddit_screenshot import take_reddit_screenshot
from subtitle_generator import generate_audio_with_subtitles_sync, VOICE_PRESETS
from ffmpeg_composer import compose_video_with_ffmpeg

# --- V3 Configuration ---
SUBREDDIT = "AskReddit"
VIDEO_TITLE_PREFIX = "Reddit Asks: "
AUDIO_SPEED_RATE = "+10%"  # edge-tts rate for 1.1x speed (reduced from +30% for more natural pace)
VOICE = VOICE_PRESETS["male_en"]  # Default voice
PEXELS_SEARCH_QUERY = None  # None = random query

# SEO-optimized tags and hashtags
VIDEO_TAGS = [
    "reddit", "askreddit", "reddit stories", "reddit story time",
    "ask reddit", "shorts", "youtube shorts",
    "viral", "storytelling", "reddit asks", "reddit thread",
    "reddit compilation", "trending"
]

VIDEO_HASHTAGS = [
    "#redditstories",
    "#askreddit", 
    "#shorts",
    "#viral",
    "#trending"
]
# ---------------------


def build_narration_text(post_data: dict) -> str:
    """
    Build complete narration text from post title and top comments.
    
    The Turkish specification emphasizes authentic Reddit appearance,
    so we keep the text natural and conversational.
    """
    title = post_data['title']
    subreddit = post_data.get('subreddit', 'AskReddit')
    comments = post_data.get('comments', [])
    
    # Start with title
    text_parts = [f"From r/{subreddit}: {title}"]
    
    # Add top comments (limit to 3-5 for reasonable video length)
    max_comments = 5
    for i, comment in enumerate(comments[:max_comments], 1):
        author = comment.get('author', 'unknown')
        body = comment.get('body', '')
        
        # Clean up comment text
        body = body.replace('\n', ' ').strip()
        
        # Skip very short or very long comments
        if len(body) < 20 or len(body) > 500:
            continue
        
        text_parts.append(f"Comment from {author}: {body}")
    
    return " ".join(text_parts)


def main():
    """
    Main orchestration following Turkish specification workflow:
    
    1. CRON Trigger → Start
    2. Reddit Scrape (existing code)
    3. Pexels Video Download (NEW)
    4. Playwright Screenshot (NEW)
    5. edge-tts with Subtitles (NEW)
    6. FFmpeg filter_complex Assembly (NEW)
    7. YouTube Upload (existing code)
    """
    print("=" * 60)
    print("🤖 Reddit-to-YouTube Shorts Bot V3 (Turkish Specification)")
    print("=" * 60)
    print()
    
    # -------------------------------------------------------------------------
    # STEP 1: Fetch Fresh Reddit Post
    # -------------------------------------------------------------------------
    print("📋 Step 1/7: Fetching Reddit post...")
    post_data = reddit_scraper.get_top_reddit_post(SUBREDDIT)
    
    if not post_data:
        print("❌ No suitable Reddit post found. Exiting.")
        sys.exit(1)
    
    title = post_data['title']
    url = post_data['url']
    subreddit = post_data.get('subreddit', SUBREDDIT)
    
    print(f"✅ Post selected:")
    print(f"   Title: {title}")
    print(f"   URL: {url}")
    print(f"   Subreddit: r/{subreddit}")
    print(f"   Comments: {len(post_data.get('comments', []))}")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 2: Download Pexels Background Video
    # -------------------------------------------------------------------------
    print("📋 Step 2/7: Downloading Pexels background video...")
    
    query = PEXELS_SEARCH_QUERY if PEXELS_SEARCH_QUERY else get_random_query()
    print(f"   Using query: {query}")
    
    background_video = download_pexels_video(
        query=query,
        output_file="background.mp4"
    )
    
    if not background_video:
        print("❌ Failed to download Pexels video. Exiting.")
        sys.exit(1)
    
    print(f"✅ Background video ready: {background_video}")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 3: Take Playwright Screenshot of Reddit Post
    # -------------------------------------------------------------------------
    print("📋 Step 3/7: Taking Reddit screenshot with Playwright...")
    
    screenshot_image = take_reddit_screenshot(
        post_url=url,
        output_file="post.png",
        width=1080,
        height=1920
    )
    
    if not screenshot_image:
        print("❌ Failed to take Reddit screenshot. Exiting.")
        sys.exit(1)
    
    print(f"✅ Screenshot ready: {screenshot_image}")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 4: Generate Audio and Subtitles with edge-tts
    # -------------------------------------------------------------------------
    print("📋 Step 4/7: Generating audio and subtitles with edge-tts...")
    
    narration_text = build_narration_text(post_data)
    print(f"   Narration length: {len(narration_text)} characters")
    
    # Try edge-tts first
    result = generate_audio_with_subtitles_sync(
        text=narration_text,
        audio_file="audio.mp3",
        subtitle_file="subtitles.srt",
        voice=VOICE,
        rate=AUDIO_SPEED_RATE
    )
    
    if not result:
        # Fallback to gTTS if edge-tts fails
        print("⚠️  edge-tts failed, falling back to gTTS...")
        try:
            from gtts import gTTS
            from audio_utils import speed_up_audio
            
            # Generate audio with gTTS
            tts = gTTS(text=narration_text, lang='en', slow=False)
            temp_audio = "audio_temp.mp3"
            tts.save(temp_audio)
            
            # Speed it up to 1.1x (matching edge-tts +10% rate)
            audio_file = speed_up_audio(temp_audio, "audio.mp3", speed=1.1)
            subtitle_file = None  # No subtitles with gTTS
            
            if not audio_file:
                print("❌ Failed to generate audio with fallback method. Exiting.")
                sys.exit(1)
                
            print(f"✅ Audio generated with gTTS (fallback)")
            
        except Exception as e:
            print(f"❌ Fallback audio generation failed: {e}")
            sys.exit(1)
    else:
        audio_file, subtitle_file = result
    
    print(f"✅ Audio ready: {audio_file}")
    print(f"✅ Subtitles ready: {subtitle_file}")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 5: Compose Final Video with FFmpeg filter_complex
    # -------------------------------------------------------------------------
    print("📋 Step 5/7: Composing video with FFmpeg filter_complex...")
    
    final_video = compose_video_with_ffmpeg(
        background_video=background_video,
        screenshot_image=screenshot_image,
        subtitle_file=subtitle_file,
        audio_file=audio_file,
        output_file="final_short.mp4",
        screenshot_position="top"
    )
    
    if not final_video:
        print("❌ Failed to compose final video. Exiting.")
        sys.exit(1)
    
    print(f"✅ Final video ready: {final_video}")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 6: Prepare YouTube Metadata
    # -------------------------------------------------------------------------
    print("📋 Step 6/7: Preparing YouTube metadata...")
    
    # Create SEO-optimized title (max 100 chars for Shorts)
    youtube_title = f"{VIDEO_TITLE_PREFIX}{title[:80]}"
    if len(youtube_title) > 100:
        youtube_title = youtube_title[:97] + "..."
    
    # Create description with hashtags
    youtube_description = f"{title}\n\n"
    youtube_description += f"Source: {url}\n\n"
    youtube_description += " ".join(VIDEO_HASHTAGS)
    
    print(f"   Title: {youtube_title}")
    print(f"   Tags: {len(VIDEO_TAGS)} tags")
    print()
    
    # -------------------------------------------------------------------------
    # STEP 7: Upload to YouTube
    # -------------------------------------------------------------------------
    print("📋 Step 7/7: Uploading to YouTube...")
    
    # Load YouTube credentials from environment variables
    client_secrets_content = os.environ.get('CLIENT_SECRETS_CONTENT')
    youtube_token_content = os.environ.get('YOUTUBE_TOKEN_CONTENT')
    
    if not client_secrets_content or not youtube_token_content:
        print("❌ YouTube credentials not found in environment variables.")
        print("   Make sure CLIENT_SECRETS_CONTENT and YOUTUBE_TOKEN_CONTENT are set.")
        sys.exit(1)
    
    # Write credentials to temporary files
    with open(youtube_uploader.CLIENT_SECRETS_FILE, 'w') as f:
        f.write(client_secrets_content)
    with open(youtube_uploader.TOKEN_FILE, 'w') as f:
        f.write(youtube_token_content)
    print("   YouTube credentials loaded")
    
    # Authenticate with YouTube
    youtube_service = youtube_uploader.get_authenticated_service()
    if not youtube_service:
        print("❌ YouTube authentication failed. Exiting.")
        sys.exit(1)
    
    # Upload video
    success = youtube_uploader.upload_video(
        youtube_service=youtube_service,
        file_path=final_video,
        title=youtube_title,
        description=youtube_description,
        tags=VIDEO_TAGS
    )
    
    if success:
        print("✅ Video uploaded successfully!")
        
        # Mark post as used
        with open(reddit_scraper.USED_POSTS_FILE, 'a') as f:
            f.write(f"{post_data['id']}\n")
        print(f"   Post marked as used: {post_data['id']}")
    else:
        print("❌ Upload failed.")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Bot completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
