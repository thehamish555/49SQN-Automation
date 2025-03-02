import streamlit as st
import streamlit_pdf_viewer as pdf_viewer
import os

if 'manuals' not in st.session_state:
    if st.session_state.is_local:
        st.session_state.manuals_path = './resources/manuals'
    else:
        st.session_state.manuals_path = './frontend/website/resources/manuals'
    st.session_state.manuals = os.listdir(st.session_state.manuals_path)
    st.session_state.manuals.sort()
if 'manual_count' not in st.session_state:
    st.session_state.manual_count = 0

@st.cache_data
def get_data(file_name):
        with open(f'{st.session_state.manuals_path}/{file_name}', 'rb') as file:
            return file.read()


try:
    @st.dialog('File Preview', width="large")
    def view_large_pdf(file_name):
        file_data = get_data(file_name)
        st.write(f'Viewing: *{file_name.removesuffix('.pdf')}*')
        st.download_button('Download PDF', data=file_data, file_name=file_name, mime='application/octet-stream', icon=':material/download:')
        pdf_viewer.pdf_viewer(file_data, width=1000, render_text=True)
except AttributeError:
    pass


st.toggle('Display as links', key='display_as_links', value=False, help='Toggle between displaying documents as links or buttons', disabled=True)
cols = st.columns(3)

with cols[0]:
    st.write('### Manuals')
    search = st.text_input('Search', key='search', placeholder='Search for Manuals...', help='Search for a specific manual')
    manuals = [m for m in st.session_state.manuals if search.lower() in m.lower().removesuffix('.pdf')]
    st.caption(f'*Showing {len(manuals[st.session_state.manual_count:st.session_state.manual_count + 10])}/{len(st.session_state.manuals)} manuals*')
    for manual in manuals[st.session_state.manual_count:st.session_state.manual_count + 10]:
        if st.session_state.display_as_links:
            st.write(f'[{manual.removesuffix(".pdf")}]({manual})')
        else:
            if st.button(manual.removesuffix('.pdf'), type='tertiary', help='View this manual'):
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

'---'

st.write('#### Quick Links')
st.write('- [Cadet Net 170C](https://www.cadetnet.org.nz/7-training/nzcf-170c/)')
