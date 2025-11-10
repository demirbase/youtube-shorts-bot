# authenticate.py
# This script is for LOCAL, ONE-TIME USE ONLY.
# Run this on your local machine to generate 'token.json'.
# DO NOT run this in GitHub Actions.
# DO NOT commit 'client_secrets.json' or 'token.json' to your repository.

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request

# Define the scopes. This scope allows for uploading videos.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"

def get_credentials():
    """
    Performs the OAuth 2.0 flow to get user credentials.
    """
    credentials = None

    # Check if token.json already exists
    if os.path.exists(TOKEN_FILE):
        print("Loading credentials from existing token.json file.")
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing expired credentials.")
            credentials.refresh(Request())
        else:
            print("No valid credentials found. Starting OAuth 2.0 flow.")
            # Create a flow object from the client secrets file
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            
            # Run the local server flow, which will open a browser for authorization
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())
        print(f"Credentials saved to {TOKEN_FILE}")

    return credentials

if __name__ == "__main__":
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Error: {CLIENT_SECRETS_FILE} not found.")
        print("Please download it from the Google Cloud Console and place it in this directory.")
    else:
        print("Starting authentication process...")
        get_credentials()
        print("\nAuthentication successful.")
        print(f"'{TOKEN_FILE}' has been created.")
        print("You can now add the *contents* of 'client_secrets.json' and 'token.json' as GitHub Actions secrets.")
