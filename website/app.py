import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
import platform
import json

st.session_state.beta_features = False
if 'beta_features' in st.session_state and st.session_state.beta_features:

    # import streamlit as st

    import os

    from handlers.data import loaders, config

    st.warning('You are currently viewing the new Layout. Not all features are available. To return to the old layout, please disable beta features in your account settings.', icon=':material/info:')
    st.info('This current redesign works on integrating the website with a larger database, allowing for more general use of the app.', icon=':material/info:')

    st.markdown('#### 49SQN NCO App')

    st.session_state.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    page_config = config.PageConfig(version='V1.0.2')

    lang = loaders.LanguageLoader(st.context.locale)
    _ = lang.install()
    st.session_state._ = _

    st.set_page_config(
        page_title=_('page.title'),
        page_icon=(st.session_state.BASE_PATH + '/' + 'resources/media/icon.png'),
        layout='wide',
        menu_items={
            'Get Help': None,
            'Report a bug': 'mailto:hamishlester555@gmail.com',
            'About': None
        }
    )

    try:
        pg = st.navigation(page_config.get_pages())
        pg.run()
    except AttributeError as e:
        st.warning('An error occurred, please try again later.', icon=':material/error:')

    page_config.load_ui_components()

else:
    if 'is_local' not in st.session_state:
        if not platform.processor():
            st.session_state.is_local = False
        else:
            st.session_state.is_local = True

    if st.session_state.is_local:
        st.set_page_config(
            page_title='49SQN NCO App',
            page_icon='resources/media/icon.png',
            layout='wide',
            menu_items={
                'Get Help': None,
                'Report a bug': 'mailto:hamishlester555@gmail.com',
                'About': None
            }
        )
    else: 
        st.set_page_config(
            page_title='49SQN NCO App',
            page_icon='./website/resources/media/icon.png',
            layout='wide', 
            menu_items={
                'Get Help': None,
                'Report a bug': 'mailto:hamishlester555@gmail.com',
                'About': None
            }
        )

    st.session_state.conn = st.connection('supabase', type=SupabaseConnection, ttl='60s')

    if 'users' not in st.session_state:
        st.session_state.users = execute_query(st.session_state.conn.table('users').select('*'), ttl='60s')
        st.session_state.users.data.sort(key=lambda x: x['permissions'][0] if len(x['permissions']) > 0 else 'user')
    if 'user' not in st.session_state:
        for user in st.session_state.users.data:
            if st.user.is_logged_in and st.user.email.lower() == user['email']:
                if 'beta_features' in user['settings']:
                    st.session_state.beta_features = False
                    # st.rerun()
                else:
                    st.session_state.beta_features = False
                st.session_state.user = user
                if st.session_state.is_local:
                    file = open('resources/configurations/permission_structure.json', 'r')
                else:
                    file = open('./website/resources/configurations/permission_structure.json', 'r')
                st.session_state.permissions = json.load(file)
                file.close()
                st.session_state.user['permissions_expanded'] = [perm for perms in st.session_state.user['permissions'] for perm in st.session_state.permissions[perms]]
                break
        if 'user' not in st.session_state:
            st.session_state.user = None
    if 'training_programs' not in st.session_state:
            st.session_state.training_programs = st.session_state.conn.create_signed_urls('training_programs', [file['name'] for file in st.session_state.conn.list_objects('training_programs', ttl='0s')], expires_in=3600)
    if 'syllabus' not in st.session_state:
        if st.session_state.is_local:
            st.session_state.syllabus_path = './resources/configurations/syllabus.json'
        else:
            st.session_state.syllabus_path = './website/resources/configurations/syllabus.json'
        with open(st.session_state.syllabus_path, 'r') as file:
            st.session_state.syllabus = json.load(file)
            temp_syllabus = {}
            for year in st.session_state.syllabus:
                for type in st.session_state.syllabus[year]:
                    for lesson in st.session_state.syllabus[year][type]:
                        temp_syllabus[f'{year} {type} - {lesson}'] = st.session_state.syllabus[year][type][lesson]
            st.session_state.syllabus = temp_syllabus
        st.session_state.syllabus = dict(sorted(st.session_state.syllabus.items()))

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

    if not st.user.is_logged_in:
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

    if st.session_state.is_local:
        st.logo(image='resources/media/cadets_header.png', size='large', icon_image='resources/media/logo.png')
    else:
        st.logo(image='./website/resources/media/cadets_header.png', size='large', icon_image='./website/resources/media/logo.png')
    pg = st.navigation(pages)
    pg.run()

    st.markdown('''
<style>
    .back_to_top {
        position: fixed;
        bottom: 50px;
        right: 25px;
        z-index: 900;
        background-color: #A3D5FF;
        color: #101B26;
        border: none;
        padding: 12px 20px;
        border-radius: 2rem;
        font-size: 1rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .back_to_top:hover {
        background-color: #FFD6A5;
        color: #101B26;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
        transform: translateY(-3px);
    }

    .back_to_top:active {
        transform: scale(0.98);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .back_to_top:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(163, 213, 255, 0.6);
    }
</style>

<a target="_self" href="#49-sqn-nco-app">
    <button class="back_to_top">
        ↑ Back to Top
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
        text-align: right;
        padding-right: 30px;
        padding-bottom: 90px;
        font-size: 0.9rem;
        color: #7B8A99;
        font-weight: 500;
        opacity: 0.8;
        font-family: 'Segoe UI', sans-serif;
        z-index: 800;
        transition: opacity 0.3s ease;
    }

    .footer:hover {
        opacity: 1;
    }
</style>

<div class="footer">
    <p>V1.0.2</p>
</div>
    '''
    st.markdown(footer, unsafe_allow_html=True)

    if st.session_state.beta_features:
        st.markdown('''
<style>
    .beta {
        position: fixed;
        bottom: 0;
        left: 0;
        background-color: #DDEBFF;
        color: #1F2D40;
        padding: 6px 14px;
        font-weight: 600;
        border-top-right-radius: 12px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.85rem;
        box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
        z-index: 1000000;
        opacity: 0.95;
        transition: all 0.3s ease;
    }

    .beta:hover {
        opacity: 1;
        background-color: #C8E0FF;
    }
</style>

<div class="beta">Beta Features Enabled</div>
        ''', unsafe_allow_html=True)

if st.context.url.startswith('http://localhost:'):
    '---'
    st.write('### Debugging')
    st.json(dict(sorted(st.session_state.items())))
