import streamlit as st

import json
import gettext
from st_supabase_connection import SupabaseConnection, execute_query

class LanguageLoader:
    def __init__(self, locale: str) -> None:
        self.locale = locale

    def install(self) -> str:
        try:
            lang = gettext.translation(
                domain='messages',
                localedir=st.session_state.BASE_PATH + '/resources/locales',
                languages=[self.locale],
            )
            return lang.gettext
        except FileNotFoundError:
            lang = gettext.translation(
                domain='messages',
                localedir=st.session_state.BASE_PATH + '/resources/locales',
                languages=['en-US'],
            )
            return lang.gettext


class SupabaseLoader:
    def __init__(self) -> None:
        self.supabase = st.connection('supabase', type=SupabaseConnection, ttl='60s')

        self._ = st.session_state._

        self.users = None
        self.load_users()

        self.user = self.get_user(st.user)
        self.training_programs = self.get_training_programs()
        self.syllabus = self.get_syllabus()

    def load_users(self) -> None:
        if self.users is None:
            self.users = execute_query(self.supabase.table('users').select('*'), ttl='60s')
            self.users.data.sort(key=lambda x: x['permissions'][0] if len(x['permissions']) > 0 else 'user')

    def get_user(self, user) -> dict | None:
        if not user.is_logged_in:
            st.info(self._('login.login_required'), icon=':material/error:')
            if st.button(self._('login.login'), icon=':material/login:'):
                st.login()
            else:
                st.stop()
            return None

        for u in self.users.data:
            if u['email'] == user.email.lower():
                st.session_state.beta_features = 'beta_features' in u['settings']
                u['permissions_expanded'] = [perm for perms in u['permissions'] for perm in json.load(open(st.session_state.BASE_PATH + '/resources/configurations/permission_structure.json', 'r'))[perms]]
                return u

        return None
    
    def get_training_programs(self) -> list:
        return self.supabase.create_signed_urls(
            'training_programs',
            [file['name'] for file in self.supabase.list_objects('training_programs', ttl='0s')],
            expires_in=3600
        )
    
    def get_syllabus(self) -> dict:
        syllabus_path = st.session_state.BASE_PATH + '/resources/configurations/syllabus.json'

        with open(syllabus_path, 'r') as file:
            raw_syllabus = json.load(file)

        flat_syllabus = {
            f'{year} {lesson_type} - {lesson}': details
            for year, types in raw_syllabus.items()
            for lesson_type, lessons in types.items()
            for lesson, details in lessons.items()
        }

        return dict(sorted(flat_syllabus.items()))