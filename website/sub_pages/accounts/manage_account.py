import streamlit as st
from st_supabase_connection import execute_query

cols = st.columns([1, 20], vertical_alignment='bottom')
with cols[0]:
    st.image(st.user['picture'])
with cols[1]:
    st.write(f'### Welcome *{st.session_state.SUPABASE_CONNECTION.user['name']}*')

'---'

cols = st.columns([3, 5, 1], gap='large')
with cols[0]:
    st.write('### User Information')
    st.write(f'**Full Name:** {st.session_state.SUPABASE_CONNECTION.user['name']}')
    st.write(f'**Email:** {st.session_state.SUPABASE_CONNECTION.user['email']}')
    permissions_string = ":green-badge[___]"
    for permission in st.session_state.SUPABASE_CONNECTION.user['permissions']:
        permissions_string = permissions_string.replace('___', f'{permission}')+":green-badge[___]"
    st.markdown(f'**Permissions:** {permissions_string.removesuffix("[___]")}')

    if st.button('Log out'):
        st.logout()

with cols[1]:
    st.write('### Account Settings')
    tabs = st.tabs(['Edit User', 'App Settings'])
    with tabs[0]:
        with st.form(key='edit_user', border=False, enter_to_submit=False):
            name = st.text_input('Name', value=st.session_state.SUPABASE_CONNECTION.user['name'], max_chars=50, placeholder='Name', help='Change your name')
            if st.form_submit_button('Save Changes'):
                execute_query(
                    st.session_state.SUPABASE_CONNECTION.supabase.table('users')
                    .update({'name': name})
                    .eq('email', st.session_state.SUPABASE_CONNECTION.user['email']),
                    ttl=0,
                )
                st.rerun()
    with tabs[1]:
        with st.form(key='app_settings', border=False, enter_to_submit=False):
            st.write('### Application Settings')
            beta_features = st.toggle('Enable Beta Features', value=st.session_state.beta_features, help='Enable beta features for testing purposes')
            if st.form_submit_button('Save Settings'):
                st.session_state.beta_features = beta_features
                settings = []
                if beta_features:
                    settings.append('beta_features')
                execute_query(
                    st.session_state.SUPABASE_CONNECTION.supabase.table('users')
                    .update({'settings': settings})
                    .eq('email', st.session_state.SUPABASE_CONNECTION.user['email']),
                    ttl=0,
                )
                st.rerun()