from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from db import get_cursor_as_real_dict_obj, get_cursor_w_commit

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']

def load_token_from_db() -> Credentials:
    with get_cursor_as_real_dict_obj() as c:
        c.execute("SELECT * FROM google_tokens WHERE id = %s", (1,))
        row = c.fetchone()
        row: dict = dict(row)

    # Handles this error: TypeError: can't compare offset-naive and offset-aware date times
    row["expiry"] = row['expiry'].replace(tzinfo=None)

    return Credentials(token=row["token"], refresh_token=row["refresh_token"], token_uri=row["token_uri"],
                       client_id=row["client_id"], client_secret=row["client_secret"], scopes=row["scopes"],
                       expiry=row["expiry"])

def save_token_to_db(creds):
    with get_cursor_w_commit() as c:
        c.execute('update google_tokens set token=%s, refresh_token=%s, expiry=%s', (creds.token, creds.refresh_token,
                                                                                     creds.expiry.isoformat()))


def get_creds():
    """Obtain credentials from db; if unexpired, return existing creds.
    If expired, generate an updated token, expiry, and refresh token, update the db row, and return updated creds."""
    creds: Credentials = load_token_from_db()

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_token_to_db(creds)

    return creds
