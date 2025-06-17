"""
Run this when the online app yields this error:
google.auth.exceptions.RefreshError:
    ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})
Copy & paste the net token data from token.json into secrets.toml & into the secrets.toml hosted on OnRender
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def regenerate_google_token():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials to a file
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)


if __name__ == '__main__':
    regenerate_google_token()
