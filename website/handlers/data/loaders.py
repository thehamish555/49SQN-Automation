import streamlit as st
import gettext

class LanguageLoader:
    def __init__(self, locale: str) -> None:
        self.locale = locale

    def install(self) -> str:
        try:
            lang = gettext.translation(
                domain='messages',
                localedir='./resources/locales',
                languages=[self.locale],
            )
            return lang.gettext
        except FileNotFoundError:
            lang = gettext.translation(
                domain='messages',
                localedir='./resources/locales',
                languages=['en-US'],
            )
            return lang.gettext


class UserLoader:
    def __init__(self) -> None:
        pass