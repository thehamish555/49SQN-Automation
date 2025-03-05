import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
import platform
import json

st.set_page_config(
    page_title='49SQN NCO App',
    page_icon=':material/travel:',
    layout='wide',
    menu_items={
        'Get Help': None,
        'Report a bug': 'mailto:hamishlester555@gmail.com',
        'About': None
    }
)

st.session_state.conn = st.connection('supabase', type=SupabaseConnection, ttl='60s')

if 'is_local' not in st.session_state:
    if not platform.processor():
        st.session_state.is_local = False
    else:
        st.session_state.is_local = True
if 'users' not in st.session_state:
    st.session_state.users = execute_query(st.session_state.conn.table('users').select('*'), ttl='60s')
    st.session_state.users.data.sort(key=lambda x: x['permissions'][0] if len(x['permissions']) > 0 else 'user')
if 'user' not in st.session_state:
    for user in st.session_state.users.data:
        if st.experimental_user.is_logged_in and st.experimental_user.email.lower() == user['email']:
            st.session_state.user = user
            if st.session_state.is_local:
                file = open('resources/configurations/permission_structure.json', 'r')
            else:
                file = open('./frontend/website/resources/configurations/permission_structure.json', 'r')
            st.session_state.permissions = json.load(file)
            file.close()
            st.session_state.user['permissions_expanded'] = [perm for perms in st.session_state.user['permissions'] for perm in st.session_state.permissions[perms]]
            break
    if 'user' not in st.session_state:
        st.session_state.user = None
if 'training_programs' not in st.session_state:
        st.session_state.training_programs = st.session_state.conn.create_signed_urls('training_programs', [file['name'] for file in st.session_state.conn.list_objects('training_programs', ttl='0s')], expires_in=3600)

if st.session_state.user:
    pages = {
        'Home': [
            st.Page('sub_pages/home.py', title='Home', icon=':material/home:')
        ],
        'Resources': [
            st.Page('sub_pages/resources/lesson_plans.py', title='Lesson Plans', icon=':material/docs:'),
            st.Page('sub_pages/resources/documents.py', title='Documents', icon=':material/folder:')
        ],
        'Tools': [
            st.Page('sub_pages/tools/training_program.py', title='Training Program', icon=':material/csv:'),
        ],
        'Your Account': [
            st.Page('sub_pages/accounts/manage_account.py', title='Manage Account', icon=':material/manage_accounts:')
        ]
    }
    if 'view_users' in st.session_state.user['permissions_expanded']:
        pages['Admin'] = [
            st.Page('sub_pages/accounts/manage_users.py', title='Manage Users', icon=':material/manage_accounts:')
        ]
else:
    pages = {'Home': [st.Page('sub_pages/home.py', title='Home', icon=':material/home:')]}

st.markdown('#### 49SQN NCO App')
'---'

if not st.experimental_user.is_logged_in:
    if st.button('Log in with Google'):
        st.login()
    pg = st.navigation(pages, position='hidden')
    pg.run()
    st.stop()

if st.session_state.user is None:
    st.error('You do not have permission to access this app.')
    if st.button('Log out'):
        st.logout()
    pg = st.navigation(pages, position='hidden')
    pg.run()
    st.stop()

pg = st.navigation(pages)
pg.run()

st.markdown('''
<style>
    .back_to_top {
        position: fixed;
        bottom: 50px;
        right: 25px;
        z-index: 900;
    }
</style>
<a target="_self" href="#49sqn-nco-app">
    <button class="back_to_top">
        Back to Top
    </button>
</a>
''', unsafe_allow_html=True)

st.markdown('''
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    [data-testid='stHeaderActionElements'] {display: none;}
</style>
''', unsafe_allow_html=True)

footer='''
<style>
    .footer {
        position: fixed;
        right: 0;
        bottom: 0;
        color: gray;
        text-align: right;
        padding-right: 25px;
        padding-bottom: 65px;
    }
</style>

<div class="footer">
    <p>V0.7.5</p>
</div>
'''
st.markdown(footer, unsafe_allow_html=True)

if st.session_state.is_local:
    '---'
    st.write('### Debugging')
    st.json(dict(sorted(st.session_state.items())))
