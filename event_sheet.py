from dataclasses import dataclass, field
from datetime import date, datetime

import pandas as pd
import pytz

from config import EventStatus, REG_Q_CNT, TIMEZONE
from google_drive import GoogleSheetData, get_google_sheet_event_data

@dataclass
class GoogleUser:
    display_name: str
    email_address: str
    photo_link: str = field(repr=False)

@dataclass
class EventSheet:
    google_id: str
    name: str
    mime_type: str
    web_view_link: str
    lmt_str: str
    lmb: GoogleUser
    sdf: pd.DataFrame = field(repr=False)
    qdf: pd.DataFrame = field(repr=False)

    def __post_init__(self):
        self.clean_scoring()
        # TODO: self.clean_questions()

    def clean_scoring(self):
        """ignore rows where there's no team name; convert accuracy string to a float; convert attendance to a number;
        replace empty strings with pd.NA; convert question grades to integers"""
        self.sdf = self.sdf[(self.sdf['Team Name'].notna()) & (self.sdf['Team Name'] != '')]
        self.sdf.loc[:, 'Team Accuracy'] = self.sdf['Team Accuracy'].replace('%', '', regex=True).astype(float) / 100
        self.sdf.loc[:, 'Attendance'] = self.sdf['Attendance'].apply(pd.to_numeric, errors='coerce')
        with pd.option_context("future.no_silent_downcasting", False):  # removes pandas deprecation warnings
            self.sdf = self.sdf.replace('', pd.NA).infer_objects(copy=False)

        for col in self.reg_q_scoring_cols:
            self.sdf[col] = pd.to_numeric(self.sdf[col], errors='coerce')

    @property
    def reg_q_scoring_cols(self) -> list[str]:
        return [col for col in self.sdf.columns if col.isdigit()]

    @property
    def status(self) -> EventStatus:
        if not self.last_reg_q_asked:
            return EventStatus.NOT_STARTED
        if self.last_reg_q_asked == REG_Q_CNT:
            return EventStatus.COMPLETED
        return EventStatus.IN_PROGRESS

    @property
    def event_name(self) -> str:
        """Assumes the sheet name is 'ABC Location - YYYYMMDD'"""
        return self.name[:-11]

    @property
    def accuracy(self) -> float:
        """For the regular question columns, counts the positive & negative values; returns the accuracy as .xx"""
        grades = self.sdf[self.reg_q_scoring_cols].values.ravel()
        values_series = pd.Series(grades)
        pos_cnt = (values_series > 0).fillna(False).sum()
        neg_cnt = (values_series < 0).fillna(False).sum()
        total_cnt = pos_cnt + neg_cnt
        return round(pos_cnt / (pos_cnt + neg_cnt), 2) if total_cnt else 0.00

    @property
    def last_reg_q_asked(self) -> int:
        """For the integer-named columns (the regular question categories),
        iterate backwards and return the first column with a value"""
        for col in reversed(self.reg_q_scoring_cols):
            if self.sdf[col].notna().any():
                return int(col)
        return 0

    @property
    def team_cnt(self) -> int:
        return self.sdf['Team Name'].notna().sum()

    @property
    def player_cnt(self) -> int:
        cnt = self.sdf['Attendance'].sum()
        return int(cnt) if cnt else 0

    @property
    def reg_team_cnt(self) -> int:
        return (self.sdf['Registered\nTeam Code'].str.len() > 1).sum()

    @property
    def reg_player_cnt(self) -> int:
        cnt = self.sdf[self.sdf['Registered\nTeam Code'].str.len() > 1]['Attendance'].sum()
        return int(cnt) if cnt else 0

    @property
    def lmt(self) -> datetime:
        utc_time = datetime.strptime(self.lmt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = pytz.utc.localize(utc_time)
        tz = pytz.timezone(TIMEZONE)
        return utc_time.astimezone(tz)


@dataclass
class EventSheets:
    sheets: list[EventSheet]

    def __iter__(self):
        return iter(self.sheets)

    @property
    def event_cnt(self) -> int:
        return len(self.sheets)

    @property
    def completed_cnt(self) -> int:
        return sum([1 for e in self if e.status == EventStatus.COMPLETED])

    @property
    def in_progress_cnt(self) -> int:
        return sum([1 for e in self if e.status == EventStatus.IN_PROGRESS])

    @property
    def not_started_cnt(self) -> int:
        return sum([1 for e in self if e.status == EventStatus.NOT_STARTED])

    @property
    def player_cnt(self) -> int:
        return sum([e.player_cnt for e in self])

    @property
    def team_cnt(self) -> int:
        return sum([e.team_cnt for e in self])

    @property
    def reg_player_cnt(self) -> int:
        return sum([e.reg_player_cnt for e in self])

    @property
    def reg_team_cnt(self) -> int:
        return sum([e.reg_team_cnt for e in self])

def _create_event_sheet(gsd: GoogleSheetData):
    lmb_dict = gsd.metadata['lastModifyingUser']
    lmb = GoogleUser(lmb_dict['displayName'], lmb_dict['emailAddress'], lmb_dict['photoLink'])
    return EventSheet(google_id=gsd.metadata['id'], name=gsd.metadata['name'], mime_type=gsd.metadata['mimeType'],
                      web_view_link=gsd.metadata['webViewLink'], lmt_str=gsd.metadata['modifiedTime'], lmb=lmb,
                      sdf=gsd.scoring_df, qdf=gsd.questions_df)

def create_event_sheets(event_date: date) -> EventSheets:
    return EventSheets([_create_event_sheet(sheet_data) for sheet_data in get_google_sheet_event_data(event_date)])

