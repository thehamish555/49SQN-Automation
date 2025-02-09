import streamlit as st
import platform

if not platform.processor():
    st.session_state.is_local = False
else:
    st.session_state.is_local = True

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

if st.experimental_user.is_logged_in and st.experimental_user.email in st.secrets['allowed_users']:
    pages = {
        'Home': [
            st.Page('pages/home.py', title='Home', icon=':material/home:')
        ],
        'Resources': [
            st.Page('pages/resources/lesson_plans.py', title='Lesson Plans', icon=':material/docs:')
        ],
        # 'Tools': [
        #     st.Page('pages/tools/lesson_plan_generator.py', title='Lesson Plan Generator', icon=':material/docs:'),
        #     st.Page('pages/tools/training_program_generator.py', title='Training Program Generator', icon=':material/csv:'),
        # ],
        'Your Account': [
            st.Page('pages/accounts/manage_account.py', title='Manage Account', icon=':material/manage_accounts:'),
        ]
    }
else:
    pages = {'Home': [st.Page('pages/home.py', title='Home', icon=':material/home:')]}

st.markdown('#### 49SQN NCO App')
'---'
if not st.experimental_user.is_logged_in:
    if st.button('Log in with Google'):
        st.login()
    pg = st.navigation(pages, position='hidden')
    pg.run()
    st.stop()


if st.experimental_user.email not in st.secrets['allowed_users']:
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
        bottom: 25px;
        right: 25px;
        z-index: 900;
    }
</style>
<a target="_self" href="#49sqn-portal">
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
        padding-bottom: 40px;
    }
</style>

<div class="footer">
    <p>V0.1.0</p>
</div>
'''
st.markdown(footer, unsafe_allow_html=True)