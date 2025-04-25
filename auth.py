import json
# from pathlib import Path

from config import GOOGLE_TOKEN
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
# TOKEN_FILE = Path("token.json")
# CLIENT_SECRET_FILE = Path("client_secret.json")

def get_creds() -> Credentials:
    if not GOOGLE_TOKEN:
        raise ValueError("Google OAuth token not found in environment variable 'GOOGLE_TOKEN'")

    token_info = json.loads(GOOGLE_TOKEN)

    return Credentials.from_authorized_user_info(token_info, SCOPES)
