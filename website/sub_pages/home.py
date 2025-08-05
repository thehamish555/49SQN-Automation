import streamlit as st
import pandas as pd
import requests
import io
import datetime
from st_copy_to_clipboard import st_copy_to_clipboard
import streamlit_pdf_viewer as pdf_viewer
import pymupdf


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
    if 'files' not in st.session_state:
        st.session_state.files = st.session_state.SUPABASE_CONNECTION.supabase.create_signed_urls('lesson_plans', [file['name'] for file in st.session_state.SUPABASE_CONNECTION.supabase.list_objects('lesson_plans', ttl='0s')], expires_in=3600)

    try:
        @st.dialog('File Preview', width="large")
        def view_large_pdf(file_data, file_name):
            try:
                st.write(f'Viewing: *{file_name.removesuffix('.pdf')}*')
                st.download_button('Download PDF', data=file_data, file_name=file_name, mime='application/octet-stream', icon=':material/download:')
                pdf_viewer.pdf_viewer(file_data, width=1000, render_text=True)
            except AttributeError:
                st.write(f'Viewing: *{file_name['path'].removesuffix('.pdf')}*')
                st.download_button('Download PDF', data=file_data, file_name=file_name['path'], mime='application/octet-stream', icon=':material/download:')
                pdf_viewer.pdf_viewer(file_data.getvalue(), width=1000, render_text=True)

    except AttributeError:
        pass

    @st.cache_data(ttl=3600)
    def get_data(file):
        try:
            response = requests.get(st.session_state.SUPABASE_CONNECTION.syllabus[file]['url'])
            if response.status_code == 200:
                return io.BytesIO(response.content).getvalue()
        except TypeError:
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
                        text.append(f'- **Period {i + 1}:** {df[column][num]} - {df[column][num + 1]} with {df[column][num + 2]}'.replace('nan', 'Not Specified'))
                    else:
                        if text[-1] != 'No Periods Specified':
                            text.append('No Periods Specified')
                    num += 3
        for text_ in text:
            if text_.startswith('-') and not text_.split('**')[2].split('-')[0].strip().startswith('Other'):
                if st.button(text_.lstrip('-'), type='tertiary', help='View Lesson Plan/Guide'):
                    file = next((f for f in st.session_state.files if text_.split('**')[2].split('-')[0].strip().startswith(f['path'].removesuffix('.pdf').removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                    if file is None:
                        file = next((f for f in st.session_state.SUPABASE_CONNECTION.syllabus if text_.split('**')[2].split('-')[0].strip().startswith(f.removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                    view_large_pdf(get_data(file), file)
            else:
                st.write(text_.lstrip('-'))
        if st.button('View all Lesson Plans', use_container_width=True, help='Click to view all the lesson plans or guides for this week'):
            files = []
            for text_ in text:
                if text_.startswith('-') and not text_.split('**')[2].split('-')[0].strip().startswith('Other'):
                    file = next((f for f in st.session_state.files if text_.split('**')[2].split('-')[0].strip().startswith(f['path'].removesuffix('.pdf').removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                    if file is None:
                        file = next((f for f in st.session_state.SUPABASE_CONNECTION.syllabus if text_.split('**')[2].split('-')[0].strip().startswith(f.removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                    files.append(file)
            merged_files = pymupdf.open()
            for file in files:
                merged_files.insert_pdf(pymupdf.open(stream=get_data(file)))
            pdf_bytes = io.BytesIO()
            merged_files.save(pdf_bytes)
            view_large_pdf(pdf_bytes.getvalue(), f'{column.split('.')[0]} - {df[column][0]} Report.pdf')
            pdf_bytes.seek(0)
        sub_cols = st.columns(2)
        with sub_cols[0]:
            st_copy_to_clipboard('Weekly Report\n'+'\n'.join(text).replace('###### ', '').replace('#### ', '').replace('**', ''), before_copy_label='Copy Raw Text to Clipboard', after_copy_label='Copied!')
        with sub_cols[1]:
            st_copy_to_clipboard('# Weekly Report\n'+'\n'.join(text).replace('### ', ' ').replace('###### ', '## '), before_copy_label='Copy With Styling to Clipboard', after_copy_label='Copied!')
    with cols[1]:
        training_program_files = get_training_program_names()
        df = pd.read_csv(get_data(training_program_files[-1]))
        st.markdown('### Your Upcoming Lessons', help='View your upcoming lessons based on the training program')
        user_lessons = {}
        for date in [(datetime.datetime.strptime(df['Week 1'][0], '%d/%m/%Y') + datetime.timedelta(weeks=i)).strftime('%d/%m/%Y') for i in range(len(df.columns) - 2)]:
            user_lessons[date] = []
        for column in df.columns[2:]:
            if datetime.datetime.strptime(df[column][0], '%d/%m/%Y').date() >= datetime.datetime.now().date():
                num = 2
                for year in df['Year Group'].unique():
                    if isinstance(year, str):
                        for i in range(len(df['Period'].unique())-1):
                            if isinstance(df[column][num], str) or isinstance(df[column][num + 1], str) or isinstance(df[column][num + 2], str):
                                if df[column][num+2] == st.session_state.SUPABASE_CONNECTION.user['name']:
                                    user_lessons[df[column][0]].append(f'- **Period {i + 1}:** {df[column][num]} - {df[column][num + 1]} with {year}')
                            num += 3
        for week, lessons in user_lessons.items():
            if lessons:
                st.write(f'#### {week}')
                for lesson in lessons:
                    if lesson.startswith('-') and not lesson.split('**')[2].split('-')[0].strip().startswith('Other'):
                        if st.button(lesson.lstrip('-'), type='tertiary', help='View Lesson Plan/Guide'):
                            file = next((f for f in st.session_state.files if lesson.split('**')[2].split('-')[0].strip().startswith(f['path'].removesuffix('.pdf').removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                            if file is None:
                                file = next((f for f in st.session_state.SUPABASE_CONNECTION.syllabus if lesson.split('**')[2].split('-')[0].strip().startswith(f.removeprefix('Year ').removeprefix('1').removeprefix('2').removeprefix('3').removeprefix('4').split('-')[0].strip())), None)
                            view_large_pdf(get_data(file), file)
                    else:
                        st.write(lesson.lstrip('-'))
    with cols[2]:
        '### Quick Links'
        st.page_link('sub_pages/resources/lesson_plans.py', label='Lesson Plans', icon=':material/book:', help='View and download lesson plans')
        st.page_link('sub_pages/resources/documents.py', label='Documents', icon=':material/quick_reference_all:', help='View and download documents')
        st.page_link('sub_pages/tools/training_program.py', label='Training Program', icon=':material/table:', help='View the training program')
    st.warning('Some pages are still in development')
