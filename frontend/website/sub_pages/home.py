import streamlit as st

if st.session_state.user:
    st.title('Welcome to the 49SQN Air Cadet Unit NCO Portal')
    st.write('This is a Streamlit web application that assists NCOs and Officers within the 49SQN Air Cadet Unit.')

    if st.session_state.is_local:
        st.image('resources/media/logo.png')
    else:
        st.image('./frontend/website/resources/media/logo.png')

    'Some Quick Links:'
    st.page_link('sub_pages/resources/lesson_plans.py', label='Lesson Plans', icon=':material/docs:', help='View and download lesson plans')
    st.page_link('sub_pages/resources/documents.py', label='Documents', icon=':material/folder:', help='View and download documents')
    st.page_link('sub_pages/tools/training_program.py', label='Training Program', icon=':material/csv:', help='View the training program')
    
    st.warning('Some pages are still in development')
