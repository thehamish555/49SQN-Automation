import streamlit as st
import streamlit_pdf_viewer as pdf_viewer
import pymupdf
import io
import requests
import urllib
from st_supabase_connection import SupabaseConnection

cols = st.columns([1, 3, 2], border=True)

if 'files' not in st.session_state:
    st.session_state.files = st.session_state.conn.create_signed_urls('lesson_plans', [file['name'] for file in st.session_state.conn.list_objects('lesson_plans', ttl='0s')], expires_in=3600)
if 'file' not in st.session_state:
    st.session_state['file'] = None
if 'file_name' not in st.session_state:
    st.session_state['file_name'] = None
if 'last_file' not in st.session_state:
    st.session_state['last_file'] = None
if 'pdf' not in st.session_state:
    st.session_state['pdf'] = None

st.session_state.files.sort(key=lambda x: (not x['path'].endswith('Template.pdf'), x['path']))
icons = {'Default': ':material/docs:', 'Template': ':material/docs:', 'Bush Craft': ':material/forest:',}

@st.cache_data
def get_data(file):
    try:
        response = requests.get(file['signedURL'])
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()
    except TypeError:
        response = requests.get(file)
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()


def set_large_pdf(annotation):
    if st.session_state['last_file'] != annotation['file']:
        st.session_state['last_file'] = annotation['file']
    else :
        st.session_state['last_file'] = None
    st.session_state['file'] = get_data(annotation['file'])
    st.session_state['file_name'] = annotation['name']
    st.rerun()


def unload_file():
    st.session_state['file'] = None
    st.session_state['last_file'] = None


try:
    @st.dialog(st.session_state['file_name'].removesuffix('.pdf'), width="large")
    def view_large_pdf():
        pdf_viewer.pdf_viewer(st.session_state['file'], width=1000, render_text=True)
except AttributeError:
    pass


if st.session_state.user['role'] == 'admin':
    st.sidebar.title('Admin Panel')
    st.sidebar.subheader('Manage Lesson Plans')
    with st.sidebar.form(key='submit_lesson_plan'):
        uploaded_pdf = st.file_uploader('Upload Lesson Plan', type=['pdf'])
        pdf_name = st.text_input('Lesson Plan Name', placeholder='Enter the Lesson Plan Name...', max_chars=50)
        lesson_type = st.selectbox('Lesson Plan Type', [key for key in icons.keys() if key != 'Default'])
        if st.form_submit_button('Upload Lesson Plan'):
            if not uploaded_pdf:
                st.error('Please upload a PDF file')
            elif pdf_name.strip() == '':
                st.error('Please enter a name for the Lesson Plan')
            else:
                try:
                    st.session_state.conn.upload('lesson_plans', source='local', file=uploaded_pdf, destination_path=f'/{pdf_name} - {lesson_type}.pdf')
                    st.session_state.pop('files')
                    st.session_state.conn = None
                    st.rerun()
                except Exception as e:
                    st.error('File already exists, try another name')
    with st.sidebar.form(key='remove_lesson_plan'):
        selected_file = st.selectbox('Select a Lesson Plan to Remove', [f['path'].removesuffix('.pdf') for f in st.session_state.files])
        if st.form_submit_button('Remove Lesson Plan'):
            st.session_state.conn.remove('lesson_plans', [f'{selected_file}.pdf'])
            st.session_state.pop('files')
            st.session_state.conn = None
            st.rerun()

with cols[0]:
    st.markdown('#### View Lesson Plans')
    st.toggle('Preview PDFs', key='preview_pdfs', value=False)
    if st.session_state.preview_pdfs:
        st.warning('Preview PDFs is enabled, this may slow down the page')
    else:
        unload_file()
    search = st.text_input('Search', key='search', placeholder='Search for Lesson Plans...')
    files = [f for f in st.session_state.files if search.lower() in f['path'].lower().removesuffix('.pdf')]
    st.caption(f'*Found {len(files)} files*')
    for file in files:
        try:
            icon = icons[file['path'].split(' - ')[1].removesuffix('.pdf')]
        except (KeyError, IndexError):
            icon = icons['Default']
        if st.session_state.preview_pdfs:
            with st.expander(file['path'].removesuffix('.pdf'), icon=icon):
                file_data = get_data(file)
                pdf_viewer.pdf_viewer(file_data, width=350, pages_to_render=[1], on_annotation_click=set_large_pdf, annotation_outline_size=0, annotations=[{'page': 1, 'x': 0, 'y': 0, 'width': 600, 'height': 845, 'file': file['signedURL'], 'name': file['path'], 'last_file': st.session_state['last_file']}])
                st.download_button('Download as PDF', data=file_data, file_name=file['path'], mime='application/octet-stream', icon=':material/download:')
        else:
            st.write(f'{icon} [{file['path'].removesuffix('.pdf')}]({urllib.parse.quote(file['signedURL'], safe=":/?=&")})')

with cols[1]:
    st.markdown('#### Auto fill Lesson Plan')
    with st.form(key='create_lesson', border=False, enter_to_submit=False):
        selected_file = st.selectbox('Select a Lesson Plan', [f['path'].removesuffix('.pdf') for f in st.session_state.files if not f['path'].endswith('Template.pdf')])
        date = st.date_input('Date', format="DD/MM/YYYY", value='today', min_value='today')
        instructor = st.text_input('Instructor', placeholder='Enter the Instructors Name (Rank + Last Name or Full Name)...', value=st.experimental_user.name, max_chars=50)

        if st.form_submit_button('Create Lesson Plan', on_click=unload_file):
            replacements = {
                '[DATE]': date.strftime('%d/%m/%Y'),
                '[INSTRUCTOR]': instructor
            }
            st.session_state['pdf'] = pymupdf.open(stream=get_data(st.session_state.files[[f['path'] for f in st.session_state.files].index(selected_file + '.pdf')]))
            for page in st.session_state['pdf']:
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
        st.session_state['pdf'].save(pdf_bytes)
        st.download_button('Download as PDF', data=pdf_bytes.getvalue(), file_name=f'{selected_file} - {date.strftime("%d-%m-%Y")}.pdf', mime='application/octet-stream', icon=':material/download:')
        with st.expander('Preview', icon=':material/visibility:'):
            pdf_viewer.pdf_viewer(pdf_bytes.getvalue(), width=1000, render_text=True)
        pdf_bytes.seek(0)
    except AttributeError:
        pass

with cols[2]:
    st.markdown('#### Quick Links')
    st.markdown('- [Cadet Net Lesson Plans](https://www.cadetnet.org.nz/7-training/lesson-plans/)')
    st.markdown('- [Cadet Net Training Manuals](https://www.cadetnet.org.nz/7-training/training-manuals/)')
    st.markdown('- [Cadet Net Training Resources](https://www.cadetnet.org.nz/7-training/training-resources/)')

if st.session_state['file']:
    view_large_pdf()