import streamlit as st
import streamlit_pdf_viewer as pdf_viewer
import pymupdf
import io
import requests
import urllib

cols = st.columns([3, 5, 1], gap='large')

if 'files' not in st.session_state:
    st.session_state.files = st.session_state.SUPABASE_CONNECTION.supabase.create_signed_urls('lesson_plans', [file['name'] for file in st.session_state.SUPABASE_CONNECTION.supabase.list_objects('lesson_plans', ttl='0s')], expires_in=3600)
if 'pdf' not in st.session_state:
    st.session_state['pdf'] = None
if 'file_count' not in st.session_state:
    st.session_state.file_count = 0

st.session_state.files.sort(key=lambda x: (not x['path'].endswith('Template.pdf'), x['path']))
icons = {'Default': ':material/docs:',
         'Template': ':material/docs:',
         'Aviation': 'material/flight',
         'Drill': ':material/directions_walk:',
         'Ethics': ':material/docs:',
         'Exercise Planning': ':material/school:',
         'Firearms': ':material/docs:',
         'Leadership': ':material/groups:',
         'Medical': ':material/medical_services:',
         'Navigation': ':material/explore:',
         'Operations': ':material/school:',
         'Physical Training': ':material/fitness_center:',
         'Protection': ':material/forest:',
         'Radio': ':material/radio:',
         'Systems App Learning': ':material/school:',
         'Other': ':material/docs:'}

@st.cache_data(ttl=3600)
def get_data(file):
    try:
        response = requests.get(file['signedURL'])
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()
        st.session_state.pop('files')
        st.rerun()
    except TypeError:
        response = requests.get(file)
        if response.status_code == 200:
            return io.BytesIO(response.content).getvalue()
        st.session_state.pop('files')
        st.rerun()


try:
    @st.dialog('File Preview', width="large")
    def view_large_pdf(file_data, file_name):
        st.write(f'Viewing: *{file_name.removesuffix('.pdf')}*')
        st.download_button('Download PDF', data=file_data, file_name=file_name, mime='application/octet-stream', icon=':material/download:')
        pdf_viewer.pdf_viewer(file_data, width=1000, render_text=True)
except AttributeError:
    pass


def update_search():
    st.session_state.file_count = 0



@st.dialog('Confirm Deletion', width='small')
def confirmation(file):
    st.error(f'**Are you sure you want to delete "*{file}*"?**')
    st.write('This action cannot be undone.')
    cols = st.columns(2)
    with cols[0]:
        if st.button('Cancel', use_container_width=True, help='Cancel the deletion'):
            st.rerun()
    with cols[1]:
        if st.button('**:red[Delete]**', use_container_width=True, help='Delete the lesson plan'):
            st.session_state.SUPABASE_CONNECTION.supabase.remove('lesson_plans', [f'{file}.pdf'])
            st.session_state.pop('files')
            st.rerun()


with cols[0]:
    st.write('#### Lesson Plan Viewer')
    st.toggle('Display as links', key='display_as_links', value=False, help='Toggle between displaying lesson plans as links or buttons')
    search = st.text_input('Search', key='search', placeholder='Search for Lesson Plans...', help='Search for a specific lesson plan', on_change=update_search)
    files = [f for f in st.session_state.files if search.lower() in f['path'].lower().removesuffix('.pdf')]
    st.caption(f'*Showing {len(files[st.session_state.file_count:st.session_state.file_count + 10])}/{len(st.session_state.files)} lesson plans*')
    for file in files[st.session_state.file_count:st.session_state.file_count + 10]:
        try:
            icon = icons[file['path'].split(' - ')[0].split(' ')[-1]]
        except (KeyError, IndexError):
            icon = icons['Default']
        if st.session_state.display_as_links:
            st.write(f'{icon} [{file['path'].removesuffix('.pdf')}]({urllib.parse.quote(file['signedURL'], safe=":/?=&")})')
        else:
            if st.button(file['path'].removesuffix('.pdf'), icon=icon, type='tertiary', help='View this lesson plan'):
                view_large_pdf(get_data(file), file['path'])
    sub_cols = st.columns(2)
    with sub_cols[0]:
        if st.session_state.file_count > 0:
            if st.button('Previous', icon=':material/arrow_back:', use_container_width=True, help='View the previous 10 lesson plans'):
                st.session_state.file_count -= 10
                st.rerun()
    with sub_cols[1]:
        if st.session_state.file_count + 10 < len(files):
            if st.button('Next', icon=':material/arrow_forward:', use_container_width=True, help='View the next 10 lesson plans'):
                st.session_state.file_count += 10
                st.rerun()

with cols[1]:
    tabs = st.tabs(['Autofill Lesson Plans', 'Lesson Plan Manager'])
    with tabs[0]:
        with st.form(key='create_lesson', border=False, enter_to_submit=False):
            selected_file = st.selectbox('Select a Lesson Plan', [f['path'].removesuffix('.pdf') for f in st.session_state.files if not f['path'].endswith('Template.pdf')], help='Select a lesson plan to autofill')
            date = st.date_input('Date', format="DD/MM/YYYY", value='today', min_value='today', help='Select the date for the lesson plan')
            instructor = st.text_input('Instructor', placeholder='Enter the Instructors Name (Rank + Last Name or Full Name)...', value=st.session_state.SUPABASE_CONNECTION.user['name'], max_chars=50, help='Enter the name of the instructor for the lesson plan')

            if st.form_submit_button('Create Lesson Plan', use_container_width=True, help='Create a lesson plan with the selected template'):
                replacements = {
                    '[DATE]': date.strftime('%d/%m/%Y'),
                    '[INSTRUCTOR]': instructor,
                    '[NAME]': instructor
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
            st.success(f'Lesson Plan *"{selected_file}"* Created!', icon=':material/check:')
            sub_cols = st.columns(2)
            with sub_cols[0]:
                st.download_button('Download as PDF', data=pdf_bytes.getvalue(), file_name=f'{selected_file} - {date.strftime("%d-%m-%Y")}.pdf', mime='application/octet-stream', icon=':material/download:', use_container_width=True, help='Download')
            with sub_cols[1]:
                if st.button('Preview', icon=':material/visibility:', use_container_width=True, help='Preview the lesson plan'):
                    view_large_pdf(pdf_bytes.getvalue(), selected_file+'.pdf')
            pdf_bytes.seek(0)
        except AttributeError:
            pass
    with tabs[1]:
        if 'manage_lesson_plans' in st.session_state.SUPABASE_CONNECTION.user['permissions_expanded']:
            with st.form(key='submit_lesson_plan', enter_to_submit=False):
                uploaded_pdf = st.file_uploader('Upload a Lesson Plan', type=['pdf'], help='Select a lesson plan to upload')
                pdf_name = st.selectbox('Lesson Plan For:', st.session_state.SUPABASE_CONNECTION.syllabus, help='Select a name for the lesson plan', accept_new_options=True)
                if st.form_submit_button('Upload Lesson Plan', help='Upload the lesson plan to the database'):
                    if not uploaded_pdf:
                        st.error('Please upload a PDF file', icon=':material/error:')
                    else:
                        try:
                            st.session_state.SUPABASE_CONNECTION.supabase.upload('lesson_plans', source='local', file=uploaded_pdf, destination_path=f'/{pdf_name}.pdf', overwrite='true')
                            st.session_state.pop('files')
                            st.rerun()
                        except Exception as e:
                            st.error('File already exists, try another name', icon=':material/error:')
            with st.form(key='remove_lesson_plan'):
                selected_file = st.selectbox('Select a Lesson Plan to Delete', [f['path'].removesuffix('.pdf') for f in st.session_state.files], help='Select a lesson plan to remove')
                if st.form_submit_button('**:red[Delete Lesson Plan]**', help='Delete the selected lesson plan'):
                    confirmation(selected_file)
        else:
            st.warning('You do not have permission to access this tab')

'---'

st.write('#### Quick Links')
st.write('- [Cadet Net Lesson Plans](https://www.cadetnet.org.nz/7-training/lesson-plans/)')
st.write('- [Cadet Net Training Manuals](https://www.cadetnet.org.nz/7-training/training-manuals/)')
st.write('- [Cadet Net Training Resources](https://www.cadetnet.org.nz/7-training/training-resources/)')
