from datetime import date, datetime, timedelta
from enum import StrEnum
# import os

# from dotenv import load_dotenv  # pip install python-dotenv
import pytz
import streamlit as st

# load_dotenv()

class EventStatus(StrEnum):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

class SheetName(StrEnum):
    SCORING = 'Scoring'
    QUESTIONS = 'Questions'


TIMEZONE = 'US/Eastern'

def localize_utc(utc_dt: datetime, timezone_str: str = TIMEZONE) -> datetime:
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    target_tz = pytz.timezone(timezone_str)
    return utc_dt.astimezone(target_tz)


EVENTS_FOLDER_ID = st.secrets['google_drive']['EVENTS_FOLDER_ID']
GOOGLE_TOKEN = st.secrets['google_token']['GOOGLE_TOKEN']

REG_Q_CNT = 20

NOW = localize_utc(datetime.now(pytz.utc))
TODAY = NOW.date()
YESTERDAY = TODAY - timedelta(1)
