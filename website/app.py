import streamlit as st

import os

from handlers.data.PageConfig import PageConfig
from handlers.data.LanguageLoader import LanguageLoader
from handlers.data.SupabaseLoader import SupabaseLoader

# Used so that the files are loaded on both a local machine and the cloud
st.session_state.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load the language to be used for text display | Default to english
lang = LanguageLoader(st.session_state.get('locale', 'en-US'))
if '_' not in st.session_state:
    _ = lang.install()
    st.session_state._ = _
else:
    _ = st.session_state._

# Set the page configuration
# - version: The current app version
page_config = PageConfig(version='V1.5.8')

# Load the cloud database
if 'SUPABASE_CONNECTION' not in st.session_state:
    st.session_state.SUPABASE_CONNECTION = SupabaseLoader()

# Load extra UI components
page_config.load_ui_components()

try:
    # Display the logo
    st.logo(
        image=st.session_state.BASE_PATH + '/resources/media/cadets_header.png',
        size='large',
        icon_image=st.session_state.BASE_PATH + '/resources/media/logo.png'
    )
    # Attempt to run the application pages
    st.navigation(page_config.get_pages()).run()
except AttributeError as e:
    st.warning(_('errors.general'), icon=':material/error:')
    st.error(e)

# Debugging information
if st.context.url.startswith('http://localhost:'):
    '---'
    st.write('### '+(_('debugging.title')))
    st.json(dict(sorted(st.session_state.items())))
    st.json(st.session_state.SUPABASE_CONNECTION.user)