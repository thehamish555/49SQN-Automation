import streamlit as st
import pandas as pd
import requests
import io
import datetime
from st_copy_to_clipboard import st_copy_to_clipboard


def get_training_program_names():        
    training_program_files = []
    for file in st.session_state.SUPABASE_CONNECTION.training_programs:
        if file['path'] == 'active_training_programs.csv':
            active_training_programs = pd.read_csv(get_data(file))
    for file in st.session_state.SUPABASE_CONNECTION.training_programs:
        if file['path'] != 'active_training_programs.csv':
            file_name = file['path']
            file_name = file_name.removesuffix('.csv')
            split_file_name = file_name.split('_')
            year = split_file_name[0]
            term = split_file_name[1]
            file_renamed = f'{year}: Term {term}'
            for name, is_active in zip(active_training_programs['name'], active_training_programs['active']):
                if name == file_renamed and is_active == True:
                    training_program_files.append(file)
    return training_program_files


if st.session_state.SUPABASE_CONNECTION.user:
    @st.cache_data(ttl=3600)
    def get_data(file):
        response = requests.get(file['signedURL'])
        if response.status_code == 200:
            return io.BytesIO(response.content)
        st.session_state.pop('training_programs')
        st.session_state.conn = None
        st.rerun()

    cols = st.columns([1, 13])
    with cols[0]:
        st.image(st.session_state.BASE_PATH + '/resources/media/logo.png')
    with cols[1]:
        st.title('49SQN NCO Portal')
        st.write('This portal is used to assist NCOs and Officers within the 49SQN Air Cadet Unit.')
    
    '---'
    
    cols = st.columns(3, gap='large')
    with cols[0]:
        training_program_files = get_training_program_names()
        df = pd.read_csv(get_data(training_program_files[-1]))
        st.markdown('### Weekly Report', help='View the weekly report based on the training program')
        next_date = None
        for date in [(datetime.datetime.strptime(df['Week 1'][0], '%d/%m/%Y') + datetime.timedelta(weeks=i)).strftime('%d/%m/%Y') for i in range(len(df.columns) - 2)]:
            if datetime.datetime.strptime(date, '%d/%m/%Y') >= datetime.datetime.strptime(datetime.datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y'):
                next_date = date
                break
        for column in df.columns:
            if df[column][0] == next_date:
                break
        text = [f'###### {column.split('.')[0]} - {df[column][0]}']
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
                    if isinstance(df[column][num], str) or isinstance(df[column][num + 1], str) or isinstance(df[column][num + 2], str):
                        text.append(f'**Period {i + 1}:** {df[column][num]} - {df[column][num + 1]} with {df[column][num + 2]}'.replace('nan', 'Not Specified'))
                    else:
                        if text[-1] != 'No Periods Specified':
                            text.append('No Periods Specified')
                    num += 3
        for text_ in text:
            st.write(text_)
        sub_cols = st.columns(2)
        with sub_cols[0]:
            st_copy_to_clipboard('Weekly Report\n'+'\n'.join(text).replace('###### ', '').replace('#### ', '').replace('**', ''), before_copy_label='Copy Raw Text to Clipboard', after_copy_label='Copied!')
        with sub_cols[1]:
            st_copy_to_clipboard('# Weekly Report\n'+'\n'.join(text).replace('### ', ' ').replace('###### ', '## '), before_copy_label='Copy With Styling to Clipboard', after_copy_label='Copied!')
    with cols[1]:
        '### Quick Links'
        st.page_link('sub_pages/resources/lesson_plans.py', label='Lesson Plans', icon=':material/docs:', help='View and download lesson plans')
        st.page_link('sub_pages/resources/documents.py', label='Documents', icon=':material/folder:', help='View and download documents')
        st.page_link('sub_pages/tools/training_program.py', label='Training Program', icon=':material/csv:', help='View the training program')
    st.warning('Some pages are still in development')
