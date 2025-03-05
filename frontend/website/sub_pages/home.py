import streamlit as st
import pandas as pd
import requests
import io
import datetime
from st_copy_to_clipboard import st_copy_to_clipboard


if st.session_state.user:
    @st.cache_data(ttl=3600)
    def get_data(file):
        response = requests.get(file['signedURL'])
        if response.status_code == 200:
            return io.BytesIO(response.content)

    cols = st.columns([1, 13])
    with cols[0]:
        if st.session_state.is_local:
            st.image('resources/media/logo.png')
        else:
            st.image('./frontend/website/resources/media/logo.png')
    with cols[1]:
        st.title('49SQN NCO Portal')
        st.write('This portal is used to assist NCOs and Officers within the 49SQN Air Cadet Unit.')
    
    '---'
    
    cols = st.columns(3, gap='large')
    with cols[0]:
        st.markdown('### Weekly Report', help='View the weekly report based on the training program')
        df = pd.read_csv(get_data(st.session_state.training_programs[0]))
        next_date = None
        for date in [(datetime.datetime.strptime(df['Week 1'][0], '%d/%m/%Y') + datetime.timedelta(weeks=i)).strftime('%d/%m/%Y') for i in range(len(df.columns) - 2)]:
            if datetime.datetime.strptime(date, '%d/%m/%Y') >= datetime.datetime.strptime(datetime.datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y'):
                next_date = date
                break
        for column in df.columns:
            if df[column][0] == next_date:
                break
        text = [f'###### {column} - {df[column][0]}']
        if isinstance(df[column][1], str):
            text.append(f'###### Dress: {df[column][1]}')
        else:
            text.append('###### Dress: Not Specified')
        num = 2
        for year in df['Year Group'].unique():
            if isinstance(year, str):
                text.append('')
                text.append(f'#### {year}')
                for i in range(len(df['Period'].unique())-1):
                    text.append(f'**Period {i + 1}:** {df[column][num]} - {df[column][num + 1]} with {df[column][num + 2]}')
                    num += 3
        for text_ in text:
            st.write(text_)
        st_copy_to_clipboard('\n'.join(text).replace('###### ', '').replace('#### ', '').replace('**', ''), before_copy_label='Copy to Clipboard', after_copy_label='Copied!')
    with cols[1]:
        '### Quick Links'
        st.page_link('sub_pages/resources/lesson_plans.py', label='Lesson Plans', icon=':material/docs:', help='View and download lesson plans')
        st.page_link('sub_pages/resources/documents.py', label='Documents', icon=':material/folder:', help='View and download documents')
        st.page_link('sub_pages/tools/training_program.py', label='Training Program', icon=':material/csv:', help='View the training program')
    st.warning('Some pages are still in development')
