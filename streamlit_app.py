from datetime import date, datetime, timedelta

import gspread
import pandas as pd
import streamlit as st

from config import TODAY, NOW
from event_sheet import EventSheets, create_event_sheets

RUN_EVERY_X_MINUTES = 4

st.set_page_config(layout="wide",
                   page_title='Live Event Monitor', page_icon='https://whattrivia.com/favicon.ico')

def get_data(e_date: date) -> EventSheets:
    try:
        return create_event_sheets(e_date)
    except gspread.exceptions.APIError:
        st.warning("Whoa, hey, slow down there, partner. I can only refresh once per minute.")
        st.stop()

def create_dashboard_df(event_sheets: EventSheets) -> pd.DataFrame:
    events = []
    for s in event_sheets:
        event_dict = {'google_id': s.google_id, 'event_name': s.event_name, 'web_view_link': s.web_view_link,
                      'last_modified_time': s.lmt, 'last_modified_by': s.lmb.display_name,
                      'accuracy': s.accuracy, 'last_reg_q_asked': s.last_reg_q_asked,
                      'team_cnt': s.team_cnt, 'player_cnt': s.player_cnt,
                      'reg_team_cnt': s.reg_team_cnt, 'reg_player_cnt': s.reg_player_cnt}
        events.append(event_dict)
    my_df = pd.DataFrame(events)
    my_df.sort_values(by='last_reg_q_asked', ascending=False, inplace=True)
    return my_df


@st.fragment(run_every=f"{RUN_EVERY_X_MINUTES}m")  # run every 4 minutes
def run():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], vertical_alignment='bottom')
    col1.header("Live Event Monitor")
    event_date: date = col2.date_input('Event Date', value=TODAY)

    next_refresh = st.session_state['last_refresh'] + timedelta(minutes=RUN_EVERY_X_MINUTES + 1)
    col3.write(f"The data will auto-refresh at {next_refresh.strftime('%I:%M%p')}")

    col4.image(st.experimental_user.picture, width=50)

    with st.spinner("Cooking ..."):
        es = get_data(event_date)

    if not es.event_cnt:
        st.write("There are no event sheets found for this date")
        return

    dashboard_df: pd.DataFrame = create_dashboard_df(es)

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric('Total Events', es.event_cnt, border=True)
    col_b.metric('Completed', es.completed_cnt, border=True)
    col_c.metric('In-Progress', es.in_progress_cnt, border=True)
    col_d.metric('Not Started', es.not_started_cnt, border=True)
    col_a.metric('Players', es.player_cnt, border=True)
    col_b.metric('Teams', es.team_cnt, border=True)
    col_c.metric('Reg Players', es.reg_player_cnt, border=True)
    col_d.metric('Reg Teams', es.reg_team_cnt, border=True)

    st.dataframe(dashboard_df, use_container_width=True, hide_index=True,
                 column_order=('event_name', 'last_modified_time', 'last_modified_by', 'accuracy', 'last_reg_q_asked',
                               'team_cnt', 'player_cnt', 'reg_team_cnt', 'reg_player_cnt', 'web_view_link'),
                 column_config={'web_view_link': st.column_config.LinkColumn("Sheet", display_text="Open Sheet"),
                                'last_reg_q_asked': st.column_config.ProgressColumn("Last Q Asked",
                                                                                    max_value=20, format="%d"),
                                'accuracy': st.column_config.ProgressColumn("Accuracy", max_value=1.0, format='percent'),
                                'last_modified_time': st.column_config.DatetimeColumn("Last Mod", format="MM/DD/YYYY h:mma"),
                                'event_name': "Event", 'last_modified_by': "Last Modifier", 'team_cnt': "Teams",
                                'player_cnt': "Players", 'reg_team_cnt': "Reg Teams", 'reg_player_cnt': "Reg Players"
                                })


st.session_state['last_refresh'] = NOW

if not st.experimental_user.is_logged_in:
    if st.button("Authenticate via Google"):
        st.login('google')
else:
    if st.button("Logout"):
        st.logout()
    run()


# TODO:
#  write tests for a stock event sheet
#  upload to Streamlit Cloud
#  upload to nacki.app ... do i even know how to do that?


# event_sheets[0].scoring_df.to_csv('scoring.csv', index=False)
# event_sheets[0].questions_df.to_csv('questions.csv', index=False)
#

