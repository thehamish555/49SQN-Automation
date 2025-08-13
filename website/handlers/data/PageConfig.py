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

        st.html("<div id='top'><br><br></div>")

    def get_pages(self):
        admin_pages = []
        admin_pages.append(st.Page('sub_pages/accounts/manage_users.py', title=self._('page.admin.manage_users'), icon=':material/group_search:')) if st.session_state.SUPABASE_CONNECTION.user and 'view_users' in st.session_state.SUPABASE_CONNECTION.user['permissions_expanded'] else None
        return {
            self._('page.home'): [
                st.Page('sub_pages/home.py', title=self._('page.home'), icon=':material/home:')
            ],
            self._('page.resources'): [
                st.Page('sub_pages/resources/lesson_plans.py', title=self._('page.resources.lesson_plans'), icon=':material/book:'),
                st.Page('sub_pages/resources/documents.py', title=self._('page.resources.documents'), icon=':material/quick_reference_all:')
            ],
            self._('page.tools'): [
                st.Page('sub_pages/tools/training_program.py', title=self._('page.tools.training_program'), icon=':material/table:')
            ],
            self._('page.your_account'): [
                st.Page('sub_pages/accounts/manage_account.py', title=self._('page.your_account'), icon=':material/manage_accounts:')
            ],
            self._('page.admin'): admin_pages
        }
    
    def load_ui_components(self):
        # Load CSS styles
        st.html(f'{st.session_state.BASE_PATH}/resources/style.css')

        # Version footer
        st.html(f'<div class="footer">{self.version}</div>')

        # Back to top button
        st.html(
            '''
                <a target="_self" href="#top">
                    <button class="back_to_top">
                        '''
                        + self._('ui.back_to_top') +
                        '''
                    </button>
                </a>
            '''
        )

        # Beta features warning
        if st.session_state.beta_features:
            st.html('<div class="beta">'+(self._('ui.beta_features'))+'</div>')