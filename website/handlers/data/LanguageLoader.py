import streamlit as st

import gettext


class LanguageLoader:
    def __init__(self, locale: str) -> None:
        self.locale = locale

    def install(self) -> str:
        lang = gettext.translation(
            domain='messages',
            localedir=st.session_state.BASE_PATH + '/resources/locales',
            languages=[self.locale],
        )
        return lang.gettext