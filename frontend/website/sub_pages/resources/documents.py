import streamlit as st
import streamlit_pdf_viewer as pdf_viewer
import json
import requests
import io

if 'manuals' not in st.session_state:
    if st.session_state.is_local:
        st.session_state.manuals_path = './resources/configurations/manuals.json'
    else:
        st.session_state.manuals_path = './frontend/website/resources/configurations/manuals.json'
    with open(st.session_state.manuals_path, 'r') as file:
        st.session_state.manuals = json.load(file)
    st.session_state.manuals = dict(sorted(st.session_state.manuals.items()))
if 'manual_count' not in st.session_state:
    st.session_state.manual_count = 0
if 'syllabus' not in st.session_state:
    if st.session_state.is_local:
        st.session_state.syllabus_path = './resources/configurations/syllabus.json'
    else:
        st.session_state.syllabus_path = './frontend/website/resources/configurations/syllabus.json'
    with open(st.session_state.syllabus_path, 'r') as file:
        st.session_state.syllabus = json.load(file)
        temp_syllabus = {}
        for year in st.session_state.syllabus:
            for type in st.session_state.syllabus[year]:
                for lesson in st.session_state.syllabus[year][type]:
                    temp_syllabus[f'{year} {type} - {lesson}'] = st.session_state.syllabus[year][type][lesson]
        st.session_state.syllabus = temp_syllabus
    st.session_state.syllabus = dict(sorted(st.session_state.syllabus.items()))
if 'syllabus_count' not in st.session_state:
    st.session_state.syllabus_count = 0

@st.cache_data(ttl=3600)
def get_data(file):
    try:
        response = requests.get(st.session_state.syllabus[file]['url'])
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()
    except KeyError:
        response = requests.get(st.session_state.manuals[file])
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()


try:
    @st.dialog('File Preview', width="large")
    def view_large_pdf(file_name):
        file_data = get_data(file_name)
        st.write(f'Viewing: *{file_name.removesuffix('.pdf')}*')
        st.download_button('Download PDF', data=file_data, file_name=file_name, mime='application/octet-stream', icon=':material/download:')
        pdf_viewer.pdf_viewer(file_data, width=1000, render_text=True)
except AttributeError:
    pass


def update_search(search):
    if search == 'manuals': st.session_state.manual_count = 0
    if search == 'syllabus': st.session_state.syllabus_count = 0


st.toggle('Display as links', key='display_as_links', value=False, help='Toggle between displaying documents as links or buttons')
cols = st.columns(3)

with cols[0]:
    st.write('### Manuals')
    search = st.text_input('Search', placeholder='Search for Manuals...', help='Search for a specific manual', on_change=lambda x='manuals': update_search(x))
    manuals = [m for m in st.session_state.manuals if search.lower() in m.lower()]
    st.caption(f'*Showing {len(manuals[st.session_state.manual_count:st.session_state.manual_count + 10])}/{len(st.session_state.manuals)} manuals*')
    for manual in manuals[st.session_state.manual_count:st.session_state.manual_count + 10]:
        if st.session_state.display_as_links:
            st.write(f':material/docs: [{manual}]({st.session_state.manuals[manual]})')
        else:
            if st.button(manual, type='tertiary', help='View this manual', icon=':material/docs:'):
                view_large_pdf(manual)
    sub_cols = st.columns(2)
    with sub_cols[0]:
        if st.session_state.manual_count > 0:
            if st.button('Previous', icon=':material/arrow_back:', use_container_width=True, help='View the previous set of manuals'):
                st.session_state.manual_count -= 10
                st.rerun()
    with sub_cols[1]:
        if st.session_state.manual_count + 10 < len(manuals):
            if st.button('Next', icon=':material/arrow_forward:', use_container_width=True, help='View the next set of manuals'):
                st.session_state.manual_count += 10
                st.rerun()

with cols[1]:
    st.write('### Syllabus')
    search = st.text_input('Search', placeholder='Search for Lessons...', help='Search for a specific Lesson', on_change=lambda x='syllabus': update_search(x))
    syllabus = [s for s in st.session_state.syllabus if search.lower() in s.lower()]
    st.caption(f'*Showing {len(syllabus[st.session_state.syllabus_count:st.session_state.syllabus_count + 10])}/{len(st.session_state.syllabus)} lessons*')
    for syllabus_item in syllabus[st.session_state.syllabus_count:st.session_state.syllabus_count + 10]:
        if st.session_state.display_as_links:
            st.write(f':material/folder: [{syllabus_item}]({st.session_state.syllabus[syllabus_item]['url']})')
        else:
            if st.button(syllabus_item, type='tertiary', help='View this lesson', icon=':material/folder:'):
                view_large_pdf(syllabus_item)
    sub_cols = st.columns(2)
    with sub_cols[0]:
        if st.session_state.syllabus_count > 0:
            if st.button('Previous', icon=':material/arrow_back:', use_container_width=True, help='View the previous set of lessons'):
                st.session_state.syllabus_count -= 10
                st.rerun()
    with sub_cols[1]:
        if st.session_state.syllabus_count + 10 < len(syllabus):
            if st.button('Next', icon=':material/arrow_forward:', use_container_width=True, help='View the next set of lessons'):
                st.session_state.syllabus_count += 10
                st.rerun()

'---'

st.write('#### Quick Links')
st.write('- [Cadet Net 170C](https://www.cadetnet.org.nz/7-training/nzcf-170c/)')
