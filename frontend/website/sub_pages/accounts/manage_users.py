import streamlit as st
import pandas as pd
from st_supabase_connection import execute_query

df = pd.DataFrame(st.session_state.users.data)
cols = st.columns([3, 5, 1], gap='large')

@st.dialog('Confirm Deletion', width='small')
def confirmation(email):
    st.error(f'**Are you sure you want to delete "*{email}*"?**')
    st.write('This action cannot be undone.')
    cols = st.columns(2)
    with cols[0]:
        if st.button('Cancel', use_container_width=True, help='Cancel the deletion'):
            st.rerun()
    with cols[1]:
        if st.button('**:red[Delete]**', use_container_width=True, help='Delete the selected user'):
            execute_query(
                st.session_state.conn.table('users').delete().eq('email' , email),
                ttl=0
            )
            st.session_state.conn = None
            st.session_state.pop('users')
            st.session_state.pop('user')
            st.rerun()


with cols[0]:
    st.write('### View Users')
    st.write('')
    edited_data = st.dataframe(df,
                            column_config={
                                'name': st.column_config.TextColumn('Name', help='The name of the user'),
                                'email': st.column_config.TextColumn('Email', help='The email address of the user'),
                                'permissions': st.column_config.ListColumn('Permissions', help='The permissions of the user')
                                },
                            column_order=['name', 'email', 'permissions'],
                            hide_index=True,
                            use_container_width=True,
                            height=325)

with cols[1]:
    st.write('### Manage Users')
    tabs = st.tabs(['Add Users', 'Delete Users', 'Edit Users'])
    with tabs[0]:
        with st.form(key='create_user', border=False, enter_to_submit=False):
            name = st.text_input('Name', placeholder='Name', max_chars=50, help='Enter the name of the new user')
            email = st.text_input('Email', placeholder='Email', max_chars=50, help='Enter the email address of the new user')
            permissions = st.multiselect('Permissions', options=st.session_state.permissions, placeholder='Select Permissions', help='Select the permissions for the new user')
            if st.form_submit_button('Create User', help='Create a new user with the provided details'):
                email = email.lower()
                if email:
                    try:
                        execute_query(
                            st.session_state.conn.table('users').insert(
                                [{'name': name, 'email': email, 'permissions': permissions}],
                                count='None'
                            ),
                            ttl=0
                        )
                        st.session_state.conn = None
                        st.session_state.pop('users')
                        st.session_state.pop('user')
                        st.rerun()
                    except Exception as e:
                        st.error('Email already in use')
                else:
                    st.error('Must provide an email address')
    with tabs[1]:
        selected_email = st.selectbox('Select a User to Delete', [row['email'] for row in st.session_state.users.data])
        if st.button('Delete User'):
            confirmation(selected_email)
    with tabs[2]:
        selected_email = st.selectbox('Select a User to Edit', [row['email'] for row in st.session_state.users.data])
        name = st.text_input('Name', value=[row['name'] for row in st.session_state.users.data if row['email'] == selected_email][0], max_chars=50, help='Enter the name of the selected user')
        selected_permissions = st.multiselect('Permissions', options=st.session_state.permissions, default=[row['permissions'] for row in st.session_state.users.data if row['email'] == selected_email][0], help='Select the permissions for the selected user')
        if st.button('Edit User', help='Edit the selected user with the provided details'):
            execute_query(
                st.session_state.conn.table('users')
                .update({'name': name, 'permissions': selected_permissions})
                .eq('email', selected_email),
                ttl=0,
            )
            st.session_state.conn = None
            st.session_state.pop('users')
            st.session_state.pop('user')
            st.rerun()
