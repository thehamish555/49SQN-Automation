import streamlit as st
import pandas as pd
from st_supabase_connection import execute_query
import json

df = pd.DataFrame(st.session_state.SUPABASE_CONNECTION.users.data)
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
                st.session_state.SUPABASE_CONNECTION.supabase.table('users').delete().eq('email' , email),
                ttl=0
            )
            st.rerun()


with cols[0]:
    st.write('### View Users')
    st.write('')
    edited_data = st.dataframe(df,
                            column_config={
                                'name': st.column_config.TextColumn('Name', help='The name of the user'),
                                'email': st.column_config.TextColumn('Email', help='The email address of the user'),
                                'discord_id': st.column_config.TextColumn('Discord ID', help='The Discord ID of the user', width=200),
                                'permissions': st.column_config.ListColumn('Permissions', help='The permissions of the user', width=300)
                                },
                            column_order=['name', 'email', 'discord_id', 'permissions'],
                            hide_index=True,
                            use_container_width=True,
                            height=325)

if 'manage_users' in st.session_state.SUPABASE_CONNECTION.user['permissions_expanded']:
    with cols[1]:
        st.write('### Manage Users')
        tabs = st.tabs(['Add Users', 'Delete Users', 'Edit Users'])
        with tabs[0]:
            with st.form(key='create_user', border=False, enter_to_submit=False):
                name = st.text_input('Name', placeholder='Name', max_chars=50, help='Enter the name of the new user')
                email = st.text_input('Email', placeholder='Email', max_chars=50, help='Enter the email address of the new user')
                discord_id = st.text_input('Discord ID', placeholder='Discord ID', max_chars=50, help='Enter the Discord ID of the new user')
                permissions = st.multiselect('Permissions', options=json.load(open(st.session_state.BASE_PATH + '/resources/configurations/permission_structure.json', 'r')), placeholder='Select Permissions', help='Select the permissions for the new user')
                if st.form_submit_button('Create User', help='Create a new user with the provided details'):
                    if 'Admin' in permissions and 'Admin' not in st.session_state.SUPABASE_CONNECTION.user['permissions']:
                        st.error('Cannot grant admin permissions')
                    else:
                        email = email.lower()
                        if email:
                            try:
                                execute_query(
                                    st.session_state.SUPABASE_CONNECTION.supabase.table('users').insert(
                                        [{'name': name, 'email': email, 'discord_id': discord_id, 'permissions': permissions}],
                                        count='None'
                                    ),
                                    ttl=0
                                )
                                st.rerun()
                            except Exception as e:
                                st.error('Email already in use')
                        else:
                            st.error('Must provide an email address')
        with tabs[1]:
            selected_email = st.selectbox('Select a User to Delete', [row['email'] for row in st.session_state.SUPABASE_CONNECTION.users.data])
            if 'Admin' in [row['permissions'] for row in st.session_state.SUPABASE_CONNECTION.users.data if row['email'] == selected_email][0] and 'Admin' not in st.session_state.SUPABASE_CONNECTION.user['permissions'] and selected_email is not st.session_state.SUPABASE_CONNECTION.user['email']:
                st.error('Cannot delete an admin user')
            else:
                if st.button('Delete User'):
                    confirmation(selected_email)
        with tabs[2]:
            selected_email = st.selectbox('Select a User to Edit', [row['email'] for row in st.session_state.SUPABASE_CONNECTION.users.data])
            if 'Admin' in [row['permissions'] for row in st.session_state.SUPABASE_CONNECTION.users.data if row['email'] == selected_email][0] and 'Admin' not in st.session_state.SUPABASE_CONNECTION.user['permissions'] and selected_email is not st.session_state.SUPABASE_CONNECTION.user['email']:
                st.error('Cannot edit an admin user')
            else:
                name = st.text_input('Name', value=[row['name'] for row in st.session_state.SUPABASE_CONNECTION.users.data if row['email'] == selected_email][0], max_chars=50, help='Enter the name of the selected user')
                discord_id = st.text_input('Discord ID', value=[row['discord_id'] for row in st.session_state.SUPABASE_CONNECTION.users.data if row['email'] == selected_email][0], max_chars=50, help='Enter the Discord ID of the selected user')
                selected_permissions = st.multiselect('Permissions', options=json.load(open(st.session_state.BASE_PATH + '/resources/configurations/permission_structure.json', 'r')), default=[row['permissions'] for row in st.session_state.SUPABASE_CONNECTION.users.data if row['email'] == selected_email][0], help='Select the permissions for the selected user')
                if 'Admin' in selected_permissions and 'Admin' not in st.session_state.SUPABASE_CONNECTION.user['permissions']:
                    st.error('Cannot grant admin permissions')
                else:
                    if st.button('Edit User', help='Edit the selected user with the provided details'):
                        execute_query(
                            st.session_state.SUPABASE_CONNECTION.supabase.table('users')
                            .update({'name': name, 'discord_id': discord_id, 'permissions': selected_permissions})
                            .eq('email', selected_email),
                            ttl=0,
                        )
                        st.rerun()
