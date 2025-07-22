import streamlit as st

class PageConfig:
    def __init__(self, version: str = 'Development Release'):
        self.version = version

    def get_pages(self):
        return {
            'Home': [
                st.Page('sub_pages/redesign/home.py', title='Home', icon=':material/home:')
            ],
            'Resources': [
                st.Page('sub_pages/resources/lesson_plans.py', title='Lesson Plans', icon=':material/docs:'),
                st.Page('sub_pages/resources/documents.py', title='Documents', icon=':material/folder:')
            ],
            'Tools': [
                st.Page('sub_pages/tools/training_program.py', title='Training Program', icon=':material/csv:')
            ],
            'Your Account': [
                st.Page('sub_pages/accounts/manage_account.py', title='Manage Account', icon=':material/manage_accounts:')
            ]
        }
    
    def load_ui_components(self):
        with open(f'{st.session_state.BASE_PATH}/resources/style.css', 'r') as f:
            st.write(
                f'<style>{f.read()}</style>',
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