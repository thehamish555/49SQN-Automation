import streamlit as st
from st_supabase_connection import execute_query

cols = st.columns([1, 20], vertical_alignment='bottom')
with cols[0]:
    st.image(st.experimental_user['picture'])
with cols[1]:
    st.write(f'### Welcome *{st.session_state.user['name']}*')

'---'

cols = st.columns([3, 5, 1], gap='large')
with cols[0]:
    st.write('### User Information')
    st.write(f'**Full Name:** {st.experimental_user['name']}')
    st.write(f'**Email:** {st.session_state.user['email']}')
    st.pills('Permissions', options=st.session_state.user['permissions'], disabled=True)

    if st.button('Log out'):
        st.logout()

with cols[1]:
    st.write('### Account Settings')
    tabs = st.tabs(['Edit User', 'App Settings'])
    with tabs[0]:
        with st.form(key='edit_user', border=False, enter_to_submit=False):
            name = st.text_input('Name', value=st.session_state.user['name'], max_chars=50, placeholder='Name', help='Change your name')
            if st.form_submit_button('Save Changes'):
                execute_query(
                    st.session_state.conn.table('users')
                    .update({'name': name})
                    .eq('email', st.session_state.user['email']),
                    ttl=0,
                )
                st.session_state.conn = None
                st.session_state.pop('users')
                st.session_state.pop('user')
                st.rerun()

    with tabs[1]:
        st.info('User settings are not yet implemented.')
