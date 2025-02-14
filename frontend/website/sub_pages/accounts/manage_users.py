import streamlit as st
import pandas as pd
from st_supabase_connection import execute_query

st.write('### View Users')

df = pd.DataFrame(st.session_state.users.data)

edited_data = st.data_editor(df,
                             column_config={
                                 'email': 'Email',
                                 'role': st.column_config.SelectboxColumn('Role', options=['admin', 'user'], default='user', required=True)
                                 },     
                             num_rows='dynamic')

data = edited_data.to_dict()
paired_data = [{'email': data['email'][key], 'role': data['role'][key]} for key in data['email'].keys()]
if paired_data != st.session_state.users.data:
    try:
        execute_query(
            st.session_state.conn.table('users').upsert(
                paired_data, count='None'
            ),
            ttl=0,
        )
        existing_emails = {row['email'] for row in st.session_state.users.data}
        updated_emails = {row['email'] for row in paired_data}
        emails_to_delete = existing_emails - updated_emails
        for email in emails_to_delete:
            execute_query(
                st.session_state.conn.table('users')
                .delete()
                .eq('email', email),
                ttl=0,
            )

        st.session_state.conn = None
        st.session_state.pop('users')
        st.session_state.pop('user')
        st.rerun()
    except Exception as e:
        st.error('Must provide an email address')