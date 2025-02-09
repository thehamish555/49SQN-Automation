import streamlit as st

st.error('THIS PAGE IS STILL IN DEVELOPMENT, DO NOT USE')
st.page_link('pages/resources/lesson_plans.py', label='Have you checked if a Lesson Plan already exists? Click here to check', icon=':material/docs:')
cols = st.columns(2)

with cols[0]:
    with st.expander('Theory Lesson'):
        with st.form(key='theory_lesson', border=False, enter_to_submit=False):
            title = st.text_input('Lesson Title', placeholder='Enter the Lesson Title...')
            content = st.text_area('Lesson Content', placeholder='Enter the Lesson Content...')
            date = st.date_input('Date', format="DD/MM/YYYY", value=None, min_value='today')
            time_limit = st.time_input('Time Limit', value=None, step=300)
            instructor = st.text_input('Instructor', placeholder='Enter the Instructors name (Rank + Last Name)...')
            review = st.text_area('Review', placeholder='Enter a Revision of the previous lesson...')
            if st.form_submit_button('Create Lesson Plan'):
                pass

with cols[1]:
    with st.expander('Practical Lesson'):
        with st.form(key='practical_lesson', border=False, enter_to_submit=False):
            title = st.text_input('Lesson Title', placeholder='Enter the Lesson Title...')
            content = st.text_area('Lesson Content', placeholder='Enter the Lesson Content...')
            date = st.date_input('Date', format="DD/MM/YYYY", value=None, min_value='today')
            time_limit = st.time_input('Time Limit', value=None, step=300)
            instructor = st.text_input('Instructor', placeholder='Enter the Instructors name (Rank + Last Name)...')
            review = st.text_area('Review', placeholder='Enter a Revision of the previous lesson...')
            if st.form_submit_button('Create Lesson Plan'):
                pass