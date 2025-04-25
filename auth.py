import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = Path("token.json")
CLIENT_SECRET_FILE = Path("client_secret.json")

def get_creds() -> Credentials:
    google_token = os.getenv("GOOGLE_TOKEN")

    if not google_token:
        raise ValueError("Google OAuth token not found in environment variable 'GOOGLE_TOKEN'")

    token_info = json.loads(google_token)

    return Credentials.from_authorized_user_info(token_info, SCOPES)
