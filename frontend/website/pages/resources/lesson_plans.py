import streamlit as st
import streamlit_pdf_viewer as pdf_viewer
import pymupdf
import io

import os

# st.page_link('pages/tools/lesson_plan_generator.py', label='Looking for the Lesson Plan Generator? Click here', icon=':material/docs:')
cols = st.columns([1, 3, 2], border=True)
if st.session_state.is_local:
    path = 'resources/lesson_plans'
else:
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


def set_large_pdf(annotation):
    if st.session_state['last_file'] != annotation['file']:
        st.session_state['last_file'] = annotation['file']
    else :
        st.session_state['last_file'] = None
    st.session_state['file'] = f'{path}/{annotation['file']}'
    st.rerun()


def unload_file():
    st.session_state['file'] = None
    st.session_state['last_file'] = None


try:
    @st.dialog(st.session_state['file'].split('/')[-1].removesuffix('.pdf'), width="large")
    def view_large_pdf():
        pdf_viewer.pdf_viewer(st.session_state['file'], width=1000, render_text=True)
except AttributeError:
    pass


with cols[0]:
    st.markdown('#### View Lesson Plans')
    search = st.text_input('Search', key='search', placeholder='Search for Lesson Plans...')
    files = [f for f in files if search.lower() in f.lower().removesuffix('.pdf')]
    st.caption(f'*Found {len(files)} files*')
    for file in files:
        try:
            icon = icons[file.split(' - ')[1].removesuffix('.pdf')]
        except (KeyError, IndexError):
            icon = icons['Default']
        with st.expander(file.removesuffix('.pdf'), icon=icon):
            pdf_viewer.pdf_viewer(f'{path}/{file}', width=350, pages_to_render=[1], on_annotation_click=set_large_pdf, annotation_outline_size=0, annotations=[{'page': 1, 'x': 0, 'y': 0, 'width': 600, 'height': 845, 'file': file, 'last_file': st.session_state['last_file']}])
            st.download_button('Download as PDF', data=load_file(file), file_name=file, mime='application/octet-stream', icon=':material/download:')

with cols[1]:
    st.markdown('#### Auto fill Lesson Plan')
    with st.form(key='create_lesson', border=False, enter_to_submit=False):
        selected_file = st.selectbox('Select a Lesson Plan', [f.removesuffix('.pdf') for f in files if not f.endswith('Template.pdf')])
        date = st.date_input('Date', format="DD/MM/YYYY", value='today', min_value='today')
        instructor = st.text_input('Instructor', placeholder='Enter the Instructors Name (Rank + Last Name or Full Name)...', value=st.experimental_user.name, max_chars=50)

        if st.form_submit_button('Create Lesson Plan'):
            unload_file()
            replacements = {
                '[DATE]': date.strftime('%d/%m/%Y'),
                '[INSTRUCTOR]': instructor
            }

            pdf = pymupdf.open(f'{path}/{selected_file}.pdf')
            for page in pdf:
                for key, value in replacements.items():
                    text_instances = page.search_for(key)
                    for inst in text_instances:
                        rect = pymupdf.Rect(inst)
                        rect.y0 -= 10
                        rect.y1 += 10
                        rect.x1 += 300
                        page.add_redact_annot(rect, value, fontsize=12)
                page.apply_redactions()
            
    try:
        pdf_bytes = io.BytesIO()
        pdf.save(pdf_bytes)
        st.download_button('Download as PDF', data=pdf_bytes.getvalue(), file_name=f'{selected_file}.pdf', mime='application/octet-stream', icon=':material/download:')
        pdf_viewer.pdf_viewer(pdf_bytes.getvalue(), width=1000, render_text=True)
        pdf_bytes.seek(0)
        pdf.close()
    except NameError:
        pass

with cols[2]:
    st.markdown('#### Quick Links')
    st.markdown('- [Cadet Net Lesson Plans](https://www.cadetnet.org.nz/7-training/lesson-plans/)')
    st.markdown('- [Cadet Net Training Manuals](https://www.cadetnet.org.nz/7-training/training-manuals/)')
    st.markdown('- [Cadet Net Training Resources](https://www.cadetnet.org.nz/7-training/training-resources/)')

if st.session_state['file']:
    view_large_pdf()