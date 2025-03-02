import streamlit as st
import requests
import io
import pandas as pd
import datetime

if not st.session_state.is_local:
    st.info('This page is still in development, features are hidden.')
    st.stop()

if 'training_programs' not in st.session_state:
        st.session_state.training_programs = st.session_state.conn.create_signed_urls('training_programs', [file['name'] for file in st.session_state.conn.list_objects('training_programs', ttl='0s')], expires_in=3600)
    
@st.cache_data
def get_data(file):
    try:
        response = requests.get(file['signedURL'])
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except TypeError:
        response = requests.get(file)
        if response.status_code == 200:
            return io.BytesIO(response.content)


@st.cache_data
def extend_rows(df, var_string, var, count):
    if len(var) > 0:
        selected_indices = df.index[df[var_string].isin(var)].tolist()
        additional_indices = []
        for idx in selected_indices:
            additional_indices.extend(range(idx, min(idx + count, len(df))))
        return df.loc[additional_indices]
    return df


@st.cache_data
def color_column(val):
    return 'background-color: #FFA500'

df = pd.read_csv(get_data(st.session_state.training_programs[0]))

cols = st.columns(3)
with cols[0]:
    years = st.multiselect('Select Year Groups to Display', options=[year for year in df['Year Group'].unique() if isinstance(year, str)], help='Select the year groups to display.')
with cols[1]:
    periods = st.multiselect('Select Periods to Display', options=[period for period in df['Period'].unique() if isinstance(period, str)], help='Select the periods to display.')
with cols[2]:
    weeks = st.multiselect('Select Weeks to Display', options=df.columns[2:], help='Select the Weeks to display.')
next_date = None
for date in [(datetime.datetime.strptime(df['Week 1'][0], '%d/%m/%Y') + datetime.timedelta(weeks=i)).strftime('%d/%m/%Y') for i in range(len(df.columns) - 2)]:
    if datetime.datetime.strptime(date, '%d/%m/%Y') >= datetime.datetime.strptime(datetime.datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y'):
        next_date = date
        break
for column in df.columns:
    if df[column][0] == next_date:
        break

df = extend_rows(df, 'Year Group', years, 3).reset_index(drop=True)
df = extend_rows(df, 'Period', periods, 3).reset_index(drop=True)

if len(weeks) > 0:
    weeks.insert(0, 'Period')
    weeks.insert(0, 'Year Group')
    df = df[weeks]


df.fillna(' ', inplace=True)
try:
    st.dataframe(df.style.applymap(color_column, subset=[column]),
                hide_index=True,
                use_container_width=True)
except KeyError:
    st.dataframe(df,
                 hide_index=True,
                 use_container_width=True)