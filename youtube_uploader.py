# youtube_uploader.py
# Handles Google API authentication and video uploading.

import os
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# File paths for credentials, passed from main.py
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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
        # The 'from_authorized_user_file' method uses the refresh token
        # from token.json to get a new access token.
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES)
        
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
                 tags: list) -> bool:
    """
    Uploads a video file to YouTube.

    Args:
        youtube_service: The authenticated API service object.
        file_path: Path to the .mp4 video file.
        title: The video's title.
        description: The video's description.
        tags: A list of tags for the video.

    Returns:
        True if upload was successful, False otherwise.
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
        return False
    except Exception as e:
        print(f"An error occurred during upload: {e}")
        return False
