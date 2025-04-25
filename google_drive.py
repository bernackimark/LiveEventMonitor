from dataclasses import dataclass
from datetime import date, datetime

import google.oauth2.credentials
from googleapiclient.discovery import build, Resource
import gspread
import pandas as pd


from auth import get_creds
from config import EVENTS_FOLDER_ID, SheetName


@dataclass
class GoogleSheetData:
    metadata: dict
    questions_df: pd.DataFrame
    scoring_df: pd.DataFrame


def _get_sheets_recursively(ds, folder_id, name_match=None, matching_files=None) -> list[dict]:
    """Recursively find spreadsheets in a Drive folder whose name matches the name_match;
    returns a list of dict, ex:
    {'id': 'abc123', 'name': 'Title', 'mimeType': 'application/...spreadsheet',
     'webViewLink': 'https://sheet.google.com/xyz321', 'modifiedTime': datetime obj,
     'lastModifyingUser': {'displayName': 'cmm2093', 'emailAddress': 'b@gmail.com', 'photoLink': 'google.com/8uXQ'}}
    """

    if matching_files is None:
        matching_files = []  # Initialize the list if it's not passed in

    # List all items in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    fields = "files(id, name, mimeType, webViewLink, modifiedTime, lastModifyingUser)"
    response = ds.files().list(q=query, fields=fields).execute()

    for i in response.get('files', []):
        if i['mimeType'] == 'application/vnd.google-apps.folder' and i['name'].startswith('WhatTrivia -'):
            matching_files.extend(_get_sheets_recursively(ds, i['id'], name_match))
        elif i['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            if name_match not in i['name']:
                continue
            matching_files.append(i)

    return matching_files


def _get_scoring_and_question_data(gc: gspread.client.Client, i: dict) -> GoogleSheetData:
    """Accepts a Google Sheet Client & a file's metadata as a dictionary;
    makes 4 API calls;
    returns (sheet's metadata dict, questions dataframe, scoring dataframe """
    try:
        sheet = gc.open_by_key(i['id'])  # 1 API call
    except gspread.exceptions.APIError as e:
        raise e
    scoring_name = str(SheetName.SCORING.value)
    questions_name = str(SheetName.QUESTIONS.value)

    # Get all worksheets metadata in one call
    worksheet_list = sheet.worksheets()  # 1 API call

    # Find worksheets by title from metadata (no API calls)
    scoring_ws = next(ws for ws in worksheet_list if ws.title == scoring_name)
    questions_ws = next(ws for ws in worksheet_list if ws.title == questions_name)

    # Read the worksheet data (2 API calls total)
    sdf = pd.DataFrame(scoring_ws.get_all_records())  # 1 API call
    qdf = pd.DataFrame(questions_ws.get_all_records())  # 1 API call

    return GoogleSheetData(i, qdf, sdf)


def _get_google_spread_client_and_drive_service() -> tuple[gspread.client.Client, Resource]:
    creds: google.oauth2.credentials.Credentials = get_creds()
    drive_service = build('drive', 'v3', credentials=creds)
    return gspread.authorize(creds), drive_service


def wt_sheet_name_date(d: date) -> str:
    return d.isoformat().replace('-', '')


def get_google_sheet_event_data(event_date: date) -> list[GoogleSheetData]:
    start_time = datetime.now()
    sheet_client, ds = _get_google_spread_client_and_drive_service()
    event_sheets_meta: list[dict] = _get_sheets_recursively(ds, EVENTS_FOLDER_ID, wt_sheet_name_date(event_date))
    print(f"Retrieved {len(event_sheets_meta)} in {datetime.now() - start_time} seconds")
    return [_get_scoring_and_question_data(sheet_client, es) for es in event_sheets_meta]

