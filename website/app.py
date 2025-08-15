import streamlit as st

import os

from handlers.data.PageConfig import PageConfig
from handlers.data.LanguageLoader import LanguageLoader
from handlers.data.SupabaseLoader import SupabaseLoader

st.session_state.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

lang = LanguageLoader(st.session_state.get('locale', 'en-US'))
if '_' not in st.session_state:
    _ = lang.install()
    st.session_state._ = _
else:
    _ = st.session_state._

page_config = PageConfig(version='V1.4.2')

if 'SUPABASE_CONNECTION' not in st.session_state:
    st.session_state.SUPABASE_CONNECTION = SupabaseLoader()

page_config.load_ui_components()

try:
    st.logo(
        image=st.session_state.BASE_PATH + '/resources/media/cadets_header.png',
        size='large',
        icon_image=st.session_state.BASE_PATH + '/resources/media/logo.png'
    )
    st.navigation(page_config.get_pages()).run()
except AttributeError as e:
    st.warning(_('errors.general'), icon=':material/error:')
    st.error(e)


if st.context.url.startswith('http://localhost:'):
    '---'
    st.write('### '+(_('debugging.title')))
    st.json(dict(sorted(st.session_state.items())))
    st.json(st.session_state.SUPABASE_CONNECTION.user)