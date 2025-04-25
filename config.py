from datetime import date, timedelta
from enum import StrEnum
import os

from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

class EventStatus(StrEnum):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

class SheetName(StrEnum):
    SCORING = 'Scoring'
    QUESTIONS = 'Questions'


EVENTS_FOLDER_ID = os.getenv('EVENTS_FOLDER_ID')
REG_Q_CNT = 20
TIMEZONE = 'US/Eastern'
TODAY = date.today()
YESTERDAY = date.today() - timedelta(1)
