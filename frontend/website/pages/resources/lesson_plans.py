import streamlit as st
import streamlit_pdf_viewer as pdf_viewer

import os

st.page_link('pages/tools/lesson_plan_generator.py', label='Looking for the Lesson Plan Generator? Click here', icon=':material/docs:')
cols = st.columns([1, 1, 4])
path = './frontend/website/resources/lesson_plans'

files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
files.sort(key=lambda x: (not x.endswith('Template.pdf'), x))
if 'file' not in st.session_state:
    st.session_state['file'] = None
if 'last_file' not in st.session_state:
    st.session_state['last_file'] = None

icons = {'Default': ':material/docs:', 'Template': ':material/docs:', 'Bush Craft': ':material/forest:',}

@st.cache_data
def load_file(file):
    with open(f'{path}/{file}', 'rb') as pdf_file:
        return pdf_file.read()


def view_large_pdf(annotation):
    if st.session_state['last_file'] != annotation['file']:
        st.session_state['last_file'] = annotation['file']
    else :
        st.session_state['last_file'] = None
    st.session_state['file'] = f'{path}/{annotation['file']}'
    st.rerun()


with cols[0]:
    search = st.text_input('Search', key='search', placeholder='Search for Lesson Plans...')
    files = [f for f in files if search.lower() in f.lower().removesuffix('.pdf')]
    st.caption(f'*Found {len(files)} files*')
    for file in files:
        try:
            icon = icons[file.split(' - ')[1].removesuffix('.pdf')]
        except (KeyError, IndexError):
            icon = icons['Default']
        with st.expander(file.removesuffix('.pdf'), icon=icon):
            pdf_viewer.pdf_viewer(f'{path}/{file}', width=300, pages_to_render=[1], on_annotation_click=view_large_pdf, annotation_outline_size=0, annotations=[{'page': 1, 'x': 0, 'y': 0, 'width': 600, 'height': 845, 'file': file, 'last_file': st.session_state['last_file']}])
            st.download_button('Download as PDF', data=load_file(file), file_name=file, mime='application/octet-stream', icon=':material/download:')

with cols[2]:
    if st.session_state['file']:
        pdf_viewer.pdf_viewer(st.session_state['file'], width=1000, render_text=True)