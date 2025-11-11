# youtube_uploader.py
# Handles Google API authentication and video uploading.

import os
import shutil
import json
from datetime import datetime
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# File paths for credentials, passed from main.py
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
PENDING_UPLOADS_DIR = "pending_uploads"

def save_video_for_manual_upload(video_path: str, title: str, description: str, tags: list, post_id: str) -> str | None:
    """
    Saves a video and its metadata for manual upload later.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags
        post_id: Reddit post ID
        
    Returns:
        Path to saved video or None on failure
    """
    try:
        # Create pending uploads directory if it doesn't exist
        os.makedirs(PENDING_UPLOADS_DIR, exist_ok=True)
        
        # Create filename with timestamp and post ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        video_filename = f"{timestamp}_{post_id}_{safe_title}.mp4"
        metadata_filename = f"{timestamp}_{post_id}_metadata.json"
        
        video_dest = os.path.join(PENDING_UPLOADS_DIR, video_filename)
        metadata_dest = os.path.join(PENDING_UPLOADS_DIR, metadata_filename)
        
        # Copy video file
        shutil.copy2(video_path, video_dest)
        
        # Save metadata
        metadata = {
            "post_id": post_id,
            "title": title,
            "description": description,
            "tags": tags,
            "created_at": timestamp,
            "original_video": video_path,
            "saved_video": video_dest
        }
        
        with open(metadata_dest, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Video saved for manual upload:")
        print(f"   Video: {video_dest}")
        print(f"   Metadata: {metadata_dest}")
        print(f"   Size: {os.path.getsize(video_dest) / (1024*1024):.2f} MB")
        
        return video_dest
        
    except Exception as e:
        print(f"❌ Error saving video for manual upload: {e}")
        return None

def get_authenticated_service() -> googleapiclient.discovery.Resource | None:
    """
    Authenticates with the Google API using the token.json and client_secrets.json
    files created by main.py in the Actions environment.

    Returns:
        An authenticated YouTube API service object, or None on failure.
    """
    print("Authenticating with YouTube API...")
    credentials = None
    try:
        import json
        
        # Load credentials from token.json
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        
        # Create credentials object from the token data
        credentials = google.oauth2.credentials.Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                # Need to use client_secrets.json to refresh
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                
                # This is a bit of a workaround for the non-interactive env
                # We load the client secrets to get the client_id and client_secret
                import json
                with open(CLIENT_SECRETS_FILE, 'r') as f:
                    client_config = json.load(f)['installed']

                credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                credentials.client_id = client_config['client_id']
                credentials.client_secret = client_config['client_secret']
                
                print("Refreshing expired credentials...")
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
            else:
                print("Could not find valid credentials. Please re-run authenticate.py locally.")
                return None

        # Build the YouTube API service
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Ensure 'token.json' and 'client_secrets.json' are correct.")
        return None

def upload_video(youtube_service: googleapiclient.discovery.Resource, 
                 file_path: str, 
                 title: str, 
                 description: str, 
                 tags: list) -> bool | str:
    """
    Uploads a video file to YouTube.

    Args:
        youtube_service: The authenticated API service object.
        file_path: Path to the .mp4 video file.
        title: The video's title.
        description: The video's description.
        tags: A list of tags for the video.

    Returns:
        True if upload was successful
        False if upload failed
        "quota_exceeded" if quota limit reached (video saved, post should be marked as used)
    """
    try:
        print(f"Uploading video '{title}' to YouTube...")
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # Category 22: "People & Blogs"
            },
            "status": {
                "privacyStatus": "private"  # Can be "public", "private", or "unlisted"
            }
        }

        # Create a MediaFileUpload object
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        # Call the API to insert the video
        request = youtube_service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        # Execute the upload
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        print(f"Upload successful! Video ID: {response['id']}")
        return True

    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        
        # Check if it's a quota exceeded error
        if e.resp.status == 400 and b'uploadLimitExceeded' in e.content:
            print("\n⚠️  YouTube Upload Quota Exceeded!")
            print("   This is a temporary limit that resets at midnight Pacific Time.")
            print("   The video has been created and saved successfully.")
            print(f"   You can manually upload: {file_path}")
            print("   Marking post as used to avoid retry.")
            return "quota_exceeded"  # Special return value
        
        return False
    except Exception as e:
        print(f"An error occurred during upload: {e}")
        return False
