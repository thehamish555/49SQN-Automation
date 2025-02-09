import streamlit as st

if st.experimental_user.is_logged_in and st.experimental_user.email in st.secrets['allowed_users']:
    st.title('Welcome to the 49SQN Air Cadet Unit NCO Portal')
    st.write('This is a Streamlit web application that assists NCOs and Officers within the 49SQN Air Cadet Unit.')


    st.image('resources/media/logo.png')

    'Some Quick Links:'
    st.page_link('pages/resources/lesson_plans.py', label='Lesson Plans', icon=':material/docs:')
    st.page_link('pages/tools/lesson_plan_generator.py', label='Lesson Plan Generator', icon=':material/docs:')
    st.page_link('pages/tools/training_program_generator.py', label='Training Program Generator', icon=':material/csv:')
    
    st.warning('Some pages are still in development')