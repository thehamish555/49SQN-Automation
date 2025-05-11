import streamlit as st
import requests
import io
import pandas as pd
import datetime
    
@st.cache_data(ttl=3600)
def get_data(file):
    response = requests.get(file['signedURL'])
    if response.status_code == 200:
        return io.BytesIO(response.content)
    st.session_state.pop('training_programs')
    st.session_state.conn = None
    st.rerun()


@st.cache_data(ttl=3600)
def extend_rows(df, var_string, var, count):
    if len(var) > 0:
        selected_indices = df.index[df[var_string].isin(var)].tolist()
        additional_indices = []
        for idx in selected_indices:
            additional_indices.extend(range(idx, min(idx + count, len(df))))
        return df.loc[additional_indices]
    return df


def color_column(val):
    return f'background-color: {st.get_option('theme.borderColor')}'


def color_users(val):
    if users.__contains__(val):
        return f'background-color: {st.get_option('theme.primaryColor')}'
    

def get_training_program_names():        
    training_program_files = {}
    for file in st.session_state.training_programs:
        if file['path'] == 'active_training_programs.csv':
            active_training_programs = pd.read_csv(get_data(file))
    for file in st.session_state.training_programs:
        if file['path'] != 'active_training_programs.csv':
            file_name = file['path']
            file_name = file_name.removesuffix('.csv')
            split_file_name = file_name.split('_')
            year = split_file_name[0]
            term = split_file_name[1]
            file_renamed = f'{year}: Term {term}'
            for name, is_active in zip(active_training_programs['name'], active_training_programs['active']):
                if name == file_renamed and is_active == True:
                    training_program_files[file_renamed] = file
    return training_program_files


training_program_files = get_training_program_names()
tabs = st.tabs(['Training Program', 'Editor'])
with tabs[0]:
    training_program = st.selectbox('Select Training Program', options=training_program_files, index=len(training_program_files)-1, help='Select the training program to display.')

    try:
        df = pd.read_csv(get_data(training_program_files[training_program]))

        cols = st.columns(4)
        with cols[0]:
            years = st.multiselect('Select Year Groups to Display', options=[year for year in df['Year Group'].unique() if isinstance(year, str)], help='Select the year groups to display.')
        with cols[1]:
            periods = st.multiselect('Select Periods to Display', options=[period for period in df['Period'].unique() if isinstance(period, str)], help='Select the periods to display.')
        with cols[2]:
            weeks = st.multiselect('Select Weeks to Display', options=df.columns[2:], help='Select the Weeks to display.')
        with cols[3]:
            users = st.multiselect('Select Users to Display', options=[user['name'] for user in st.session_state.users.data], default=st.session_state.user['name'], help='Select the users to display.')

        next_date = None
        for date in [(datetime.datetime.strptime(df['Week 1'][0], '%d/%m/%Y') + datetime.timedelta(weeks=i)).strftime('%d/%m/%Y') for i in range(len(df.columns) - 2)]:
            if datetime.datetime.strptime(date, '%d/%m/%Y') >= datetime.datetime.strptime(datetime.datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y'):
                next_date = date
                break
        for column in df.columns:
            if df[column][0] == next_date:
                break

        df = extend_rows(df, 'Year Group', years, 3).reset_index(drop=True)
        df = extend_rows(df, 'Period', periods, 3).reset_index(drop=True)

        if len(weeks) > 0:
            weeks.insert(0, 'Period')
            weeks.insert(0, 'Year Group')
            df = df[weeks]


        df.fillna(' ', inplace=True)

        year_group_indices = {year: df.index[df['Year Group'] == year].tolist() for year in df['Year Group'].unique()}
        year_group_indices.pop(' ')
        for indices in year_group_indices:
            for idx in year_group_indices[indices][1:]:
                df.loc[idx, 'Year Group'] = ''
        column_config = {}
        for week in df.columns:
            column_config[week] = st.column_config.TextColumn(week, width=200)
        column_config['Year Group'] = st.column_config.TextColumn('Year Group', width=100, pinned=True)
        column_config['Period'] = st.column_config.TextColumn('Period', width=100, pinned=True)
        try:
            st.dataframe(df.style.map(color_column, subset=[column]).map(color_users),
                        hide_index=True,
                        column_config=column_config,
                        height=947)
        except KeyError:
            st.dataframe(df,
                        hide_index=True,
                        height=947)
    except KeyError:
        st.error('No active training programs available')

with tabs[1]:
    if 'manage_training_program' in st.session_state.user['permissions_expanded']:
        columns = st.columns(2)
        with columns[0]:
            for file in st.session_state.training_programs:
                if file['path'] == 'active_training_programs.csv':
                    active_TPs_df = pd.read_csv(get_data(file))
                    break
            st.write("### Active Training Programs")
            edited_data = st.data_editor(active_TPs_df,
                                         column_config={
                                             "name": st.column_config.TextColumn("Name", width=125, disabled=True),
                                             "active": st.column_config.CheckboxColumn("Active", width=100)
                                         },
                                         hide_index=True,
                                         use_container_width=False)
            if (edited_data.to_dict(orient="records") != active_TPs_df.to_dict(orient="records")):
                csv_bytes = io.BytesIO(edited_data.to_csv(index=False).encode('utf-8'))
                csv_bytes.name = "active_training_programs.csv"
                csv_bytes.type = "text/csv"
                st.session_state.conn.upload(bucket_id='training_programs',
                                            source='local',
                                            file=csv_bytes,
                                            destination_path='/active_training_programs.csv',
                                            overwrite='true')
                st.session_state.pop('training_programs')
                st.session_state.conn = None
                st.rerun()
    else:
        st.warning('You do not have permission to access this tab')