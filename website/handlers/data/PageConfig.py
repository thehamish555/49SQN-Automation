import streamlit as st


class PageConfig:
    def __init__(self, version: str = 'Development Release'):
        self.version = version
        self._ = st.session_state._

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

        st.markdown("<div id='top'></div>", unsafe_allow_html=True)

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

    def __add_component(self, component: str) -> None:
        st.write(
            component,
            unsafe_allow_html=True
        )
    
    def load_ui_components(self):
        # Load CSS styles
        with open(f'{st.session_state.BASE_PATH}/resources/style.css', 'r') as f:
            self.__add_component(f'<style>{f.read()}</style>')

        # Version footer
        self.__add_component(f'<div class="footer">{self.version}</div>')

        # Back to top button
        self.__add_component(
            '''
                <a target="_self" href="#top">
                    <button class="back_to_top">
                        ↑ Back to Top
                    </button>
                </a>
            '''
        )

        # Beta features warning
        if st.session_state.beta_features:
            self.__add_component(
                '<div class="beta">Beta Features Enabled</div>'
            )