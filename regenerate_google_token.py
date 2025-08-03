"""
Run this when the online app yields this error:
google.auth.exceptions.RefreshError:
    ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})

Note: I have not tested this.  It's possible I may have to copy & paste the returned creds and paste into db.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

from auth_google_drive import save_token_to_db
from db import get_cursor_w_commit

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']

def get_client_config_from_db():
    with get_cursor_w_commit() as c:
        c.execute("SELECT client_id, client_secret, auth_uri, token_uri, redirect_uris FROM google_oauth_clients")
        row = c.fetchone()
        client_id, client_secret, auth_uri, token_uri, redirect_uris = row

    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "redirect_uris": redirect_uris,
        }
    }


def run_oauth_consent_flow() -> dict:
    client_config = get_client_config_from_db()
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


if __name__ == "__main__":
    credentials = run_oauth_consent_flow()
    save_token_to_db(credentials)
