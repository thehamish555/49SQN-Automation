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
paired_data = [{"email": data["email"][i], "role": data["role"][i]} for i in range(len(data["email"]))]
if paired_data != st.session_state.users.data:
    try:
        execute_query(
            st.session_state.conn.table('users').upsert(
                paired_data, count='None'
            ),
            ttl=0,
        )
        st.session_state.conn = None
        st.session_state.pop('users')
        st.session_state.pop('user')
    except:
        st.error('Must provide an email address')