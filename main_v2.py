# main_v2.py
# V2 enhanced orchestration script with all new features

import os
import sys
import reddit_scraper
import youtube_uploader
from audio_utils import speed_up_audio, get_audio_duration
from background_downloader import download_background_video
from comment_image_generator import create_comment_image
from video_assembler_v2 import assemble_short_video
from gtts import gTTS

# --- V2 Configuration ---
SUBREDDIT = "AskReddit"
VIDEO_TITLE_PREFIX = "Reddit Asks: "
AUDIO_SPEED = 1.3  # 30% faster narration
USE_DYNAMIC_BACKGROUND = True  # Download Minecraft parkour videos
BACKGROUND_QUERY = "minecraft parkour gameplay no commentary"

# SEO-optimized tags and hashtags
VIDEO_TAGS = [
    "reddit", "askreddit", "reddit stories", "reddit story time",
    "ask reddit", "minecraft parkour", "shorts", "youtube shorts",
    "viral", "storytelling", "reddit asks", "reddit thread",
    "minecraft", "parkour", "reddit compilation"
]

VIDEO_HASHTAGS = [
    "#redditstories",
    "#askreddit", 
    "#shorts",
    "#minecraftparkour",
    "#viral"
]
# ---------------------

def generate_audio_for_segments(post_data: dict) -> list:
    """
    Generates separate audio files for title and comments.
    Returns list of audio file paths.
    """
    audio_files = []
    
    # 1. Generate audio for title
    print("🎤 Generating audio for title...")
    title_text = post_data['title']
    tts_title = gTTS(text=title_text, lang='en', slow=False)
    title_audio = "audio_title.mp3"
    tts_title.save(title_audio)
    
    # Speed up the audio
    title_audio_fast = speed_up_audio(title_audio, "audio_title_fast.mp3", speed=AUDIO_SPEED)
    if title_audio_fast:
        audio_files.append(title_audio_fast)
    
    # 2. Generate audio for each comment
    if 'comments' in post_data:
        for i, comment in enumerate(post_data['comments'][:3], 1):
            print(f"🎤 Generating audio for comment {i}...")
            tts_comment = gTTS(text=comment['body'], lang='en', slow=False)
            comment_audio = f"audio_comment_{i}.mp3"
            tts_comment.save(comment_audio)
            
            # Speed up
            comment_audio_fast = speed_up_audio(
                comment_audio, 
                f"audio_comment_{i}_fast.mp3", 
                speed=AUDIO_SPEED
            )
            if comment_audio_fast:
                audio_files.append(comment_audio_fast)
    
    return audio_files


def generate_seo_description(post_data: dict) -> str:
    """
    Generates SEO-optimized description with hashtags.
    """
    title = post_data['title']
    url = post_data['url']
    hashtags_str = " ".join(VIDEO_HASHTAGS)
    
    description = f"""{title}

🎮 Watch this viral Reddit story with Minecraft parkour gameplay!

This is a top post from r/AskReddit brought to you in Short form. Real stories, real reactions!

👉 Original Post: {url}

{hashtags_str}

#redditreadings #storytime #minecraft #gaming #youtubeshorts #viral #trending
    
This video was generated automatically using AI narration."""
    
    return description


def main():
    print("🚀 --- Starting Reddit-to-YouTube Bot V2 ---")
    
    # --- 1. Load Secrets from Environment ---
    print("📋 Loading credentials from environment variables...")
    client_secrets_content = os.environ.get('CLIENT_SECRETS_CONTENT')
    youtube_token_content = os.environ.get('YOUTUBE_TOKEN_CONTENT')

    if not client_secrets_content or not youtube_token_content:
        print("❌ Error: CLIENT_SECRETS_CONTENT or YOUTUBE_TOKEN_CONTENT env vars not set.")
        print("   Please ensure secrets are configured correctly in GitHub Actions.")
        sys.exit(1)

    temp_files_to_clean = [youtube_uploader.CLIENT_SECRETS_FILE, youtube_uploader.TOKEN_FILE]

    try:
        # Write temporary credential files
        with open(youtube_uploader.CLIENT_SECRETS_FILE, 'w') as f:
            f.write(client_secrets_content)
        with open(youtube_uploader.TOKEN_FILE, 'w') as f:
            f.write(youtube_token_content)
        print("✅ Temporary credential files created.")

        # --- 2. Scrape Reddit ---
        post_data = reddit_scraper.get_top_reddit_post(SUBREDDIT)
        if not post_data:
            print("⚠️  No new post found or scraping failed. Exiting gracefully.")
            return

        # --- 3. Download Background Video ---
        if USE_DYNAMIC_BACKGROUND:
            background_file = download_background_video(query=BACKGROUND_QUERY)
            if not background_file:
                print("⚠️  Failed to download background, using fallback...")
                background_file = "background.png"  # Fallback to static image
        else:
            background_file = "background.png"

        # --- 4. Generate Audio Segments (with speed enhancement) ---
        audio_files = generate_audio_for_segments(post_data)
        if not audio_files:
            print("❌ Audio generation failed. Exiting.")
            sys.exit(1)

        # --- 5. Generate Comment Images ---
        print("🎨 Generating comment overlay images...")
        image_files = []
        
        # Title image
        title_img = create_comment_image(
            text=post_data['title'],
            username=f"r/{post_data['subreddit']}",
            output_png="title.png",
            is_title=True
        )
        if title_img:
            image_files.append(title_img)
        
        # Comment images
        if 'comments' in post_data:
            for i, comment in enumerate(post_data['comments'][:3], 1):
                comment_img = create_comment_image(
                    text=comment['body'],
                    username=f"u/{comment['author']}",
                    output_png=f"comment_{i}.png",
                    is_title=False
                )
                if comment_img:
                    image_files.append(comment_img)

        if not image_files:
            print("❌ Image generation failed. Exiting.")
            sys.exit(1)

        # --- 6. Assemble Final Video with MoviePy ---
        video_file_path = assemble_short_video(
            background_clip_path=background_file,
            audio_clips_paths=audio_files,
            image_clips_paths=image_files,
            output_path="final_short.mp4"
        )
        
        if not video_file_path:
            print("❌ Video assembly failed. Exiting.")
            sys.exit(1)

        # --- 7. Prepare YouTube Upload ---
        video_title = f"{VIDEO_TITLE_PREFIX}{post_data['title']}"
        if len(video_title) > 100:
            video_title = video_title[:97] + "..."
        
        full_description = generate_seo_description(post_data)

        # --- 8. Authenticate & Upload ---
        youtube_service = youtube_uploader.get_authenticated_service()
        if not youtube_service:
            print("❌ YouTube authentication failed. Exiting.")
            sys.exit(1)

        success = youtube_uploader.upload_video(
            youtube_service,
            video_file_path,
            video_title,
            full_description,
            VIDEO_TAGS
        )
        
        if success:
            print("🎉 --- V2 Pipeline execution successful! ---")
        else:
            print("❌ --- V2 Pipeline execution failed during upload. ---")
            sys.exit(1)

    finally:
        # --- 9. Cleanup ---
        print("🧹 Cleaning up temporary files...")
        for file_path in temp_files_to_clean:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   Removed {file_path}")
        print("✅ Cleanup complete.")


if __name__ == "__main__":
    main()
