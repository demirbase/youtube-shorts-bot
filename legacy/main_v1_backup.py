# main.py
# Main orchestration script - now using V3 workflow with Turkish specification
# This file simply imports and runs the V3 implementation

from main_v3 import main

# Run the V3 bot
if __name__ == "__main__":
    main()
    
    # --- 1. Load Secrets from Environment ---
    # In GitHub Actions, secrets are loaded into env vars.
    # We must write them to temporary files for the Google API client.
    print("Loading credentials from environment variables...")
    client_secrets_content = os.environ.get('CLIENT_SECRETS_CONTENT')
    youtube_token_content = os.environ.get('YOUTUBE_TOKEN_CONTENT')

    if not client_secrets_content or not youtube_token_content:
        print("Error: CLIENT_SECRETS_CONTENT or YOUTUBE_TOKEN_CONTENT env vars not set.")
        print("Please ensure secrets are configured correctly in GitHub Actions.")
        sys.exit(1)

    temp_files_to_clean = [youtube_uploader.CLIENT_SECRETS_FILE, youtube_uploader.TOKEN_FILE]

    try:
        with open(youtube_uploader.CLIENT_SECRETS_FILE, 'w') as f:
            f.write(client_secrets_content)
        with open(youtube_uploader.TOKEN_FILE, 'w') as f:
            f.write(youtube_token_content)
        print("Temporary credential files created.")

        # --- 2. Scrape Reddit ---
        post_data = reddit_scraper.get_top_reddit_post(SUBREDDIT)
        if not post_data:
            print("No new post found or scraping failed. Exiting.")
            return  # Exit gracefully

        # --- 3. Create Video ---
        video_title = f"{VIDEO_TITLE_PREFIX}{post_data['title']}"
        # Truncate title to YouTube's 100-character limit if necessary
        if len(video_title) > 100:
            video_title = video_title[:97] + "..."
            
        video_file_path = video_creator.create_video_from_post(post_data)
        if not video_file_path:
            print("Video creation failed. Exiting.")
            sys.exit(1)

        # --- 4. Authenticate & Upload ---
        youtube_service = youtube_uploader.get_authenticated_service()
        if not youtube_service:
            print("YouTube authentication failed. Exiting.")
            sys.exit(1)

        full_description = f"{post_data['title']}\n\n{VIDEO_DESCRIPTION}\nPost URL: {post_data['url']}"
        
        success = youtube_uploader.upload_video(
            youtube_service,
            video_file_path,
            video_title,
            full_description,
            VIDEO_TAGS
        )
        
        if success:
            print("--- Pipeline execution successful! ---")
        else:
            print("--- Pipeline execution failed during upload. ---")
            sys.exit(1)

    finally:
        # --- 5. Secure Cleanup ---
        print("Cleaning up temporary files...")
        for file_path in temp_files_to_clean:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed {file_path}")
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
