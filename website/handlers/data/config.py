import streamlit as st


class PageConfig:
    def __init__(self, version: str = 'Development Release'):
        self.version = version
        self._ = st.session_state._

    def get_pages(self):
        return {
            self._('page.home'): [
                st.Page('sub_pages/home.py', title=self._('page.home'), icon=':material/home:')
            ],
            self._('page.resources'): [
                st.Page('sub_pages/resources/lesson_plans.py', title=self._('page.resources.lesson_plans'), icon=':material/docs:'),
                st.Page('sub_pages/resources/documents.py', title=self._('page.resources.documents'), icon=':material/folder:')
            ],
            self._('page.tools'): [
                st.Page('sub_pages/tools/training_program.py', title=self._('page.tools.training_program'), icon=':material/csv:')
            ],
            self._('page.your_account'): [
                st.Page('sub_pages/accounts/manage_account.py', title=self._('page.your_account'), icon=':material/manage_accounts:')
            ],
            self._('page.admin'): [
                st.Page('sub_pages/accounts/manage_users.py', title=self._('page.admin.manage_users'), icon=':material/manage_accounts:')
            ]
        }
    
    def load_ui_components(self):
        with open(f'{st.session_state.BASE_PATH}/resources/style.css', 'r') as f:
            st.write(
                f'<style>{f.read()}</style>',
                unsafe_allow_html=True
            )

        st.write(
            '<p hidden>49SQN NCO App</p>',
            unsafe_allow_html=True
        )

        # Version footer
        st.write(
            f'<div class="footer">{self.version}</div>',
            unsafe_allow_html=True
        )

        # Back to top button
        st.write(
            '''
                <a target="_self" href="#49-sqn-nco-app">
                    <button class="back_to_top">
                        ↑ Back to Top
                    </button>
                </a>
            ''',
            unsafe_allow_html=True
        )

        # Beta features warning
        if st.session_state.beta_features:
            st.write(
                '<div class="beta">Beta Features Enabled</div>',
                unsafe_allow_html=True
            )