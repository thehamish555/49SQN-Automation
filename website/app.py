import streamlit as st

import os

from handlers.data import loaders, config

st.session_state.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

lang = loaders.LanguageLoader(st.context.locale)
_ = lang.install()
st.session_state._ = _

page_config = config.PageConfig(version='V1.0.4')

st.set_page_config(
    page_title='49SQN NCO App',
    page_icon=(st.session_state.BASE_PATH + '/resources/media/icon.png'),
    layout='wide',
    menu_items={
        'Get Help': None,
        'Report a bug': 'mailto:hamishlester555@gmail.com',
        'About': None
    }
)

st.session_state.SUPABASE_CONNECTION = loaders.SupabaseLoader()

try:
    st.logo(
        image=st.session_state.BASE_PATH + '/resources/media/cadets_header.png',
        size='large',
        icon_image=st.session_state.BASE_PATH + '/resources/media/logo.png'
    )
    pg = st.navigation(page_config.get_pages())
    pg.run()
except AttributeError as e:
    st.warning(_('errors.general'), icon=':material/error:')
    st.error(e)

page_config.load_ui_components()

if st.context.url.startswith('http://localhost:'):
    '---'
    st.write('### '+(_('debugging.title')))
    st.json(dict(sorted(st.session_state.items())))
    st.json(st.session_state.SUPABASE_CONNECTION.user)