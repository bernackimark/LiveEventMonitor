from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = Path("token.json")
CLIENT_SECRET_FILE = Path("client_secret.json")

def get_creds() -> Credentials:
    """
    Retrieves the credentials for accessing Google Drive and Sheets.
    If credentials are invalid or expired, it will trigger the OAuth flow for re-authentication.
    """
    creds = None

    # Check if token file exists and is valid
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If the credentials are invalid or expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                # If expired, refresh the credentials using the refresh token
                creds.refresh(Request())
            except RefreshError:
                # If no valid credentials, run OAuth flow to get new credentials
                flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
                # creds = flow.run_local_server(port=0)  # Starts the local server and opens browser for authentication
                creds = flow.run_console()  # since Streamlit can't open a browser for auth, need use run_console()

        # Save the credentials to token.json for future use
        with TOKEN_FILE.open('w') as token:
            token.write(creds.to_json())

    return creds
