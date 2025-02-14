import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
import platform

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
    st.session_state.users.data.sort(key=lambda x: x['role'])
if 'user' not in st.session_state:
    for user in st.session_state.users.data:
        if st.experimental_user.is_logged_in and st.experimental_user.email.lower() == user['email']:
            st.session_state.user = user
            break
    if 'user' not in st.session_state:
        st.session_state.user = None

if st.session_state.user:
    pages = {
        'Home': [
            st.Page('sub_pages/home.py', title='Home', icon=':material/home:')
        ],
        'Resources': [
            st.Page('sub_pages/resources/lesson_plans.py', title='Lesson Plans', icon=':material/docs:')
        ],
        # 'Tools': [
        #     st.Page('pages/tools/training_program_generator.py', title='Training Program Generator', icon=':material/csv:'),
        # ],
        'Your Account': [
            st.Page('sub_pages/accounts/manage_account.py', title='Manage Account', icon=':material/manage_accounts:'),
        ]
    }
    if st.session_state.user['role'] == 'admin':
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
        left: 0;
        bottom: 0;
        width: 100%;
        color: gray;
        text-align: right;
        padding-right: 25px;
        padding-bottom: 65px;
    }
</style>

<div class="footer">
    <p>V0.1.0</p>
</div>
'''
st.markdown(footer, unsafe_allow_html=True)

if st.session_state.is_local:
    '---'
    st.write('### Debugging')
    st.json(dict(sorted(st.session_state.items())))