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


@st.dialog('Confirm Deletion', width='small')
def confirmation(file):
    st.error(f'**Are you sure you want to delete "*{file}*"?**')
    st.write('This action cannot be undone.')
    cols = st.columns(2)
    with cols[0]:
        if st.button('Cancel', use_container_width=True, help='Cancel the deletion'):
            st.rerun()
    with cols[1]:
        if st.button('**:red[Delete]**', use_container_width=True, help='Delete the training program'):
            file = file.replace(': ', '_').replace('Term ', '')
            st.session_state.SUPABASE_CONNECTION.supabase.remove('training_programs', [f'{file}.pdf'])
            st.rerun()


def color_column(val):
    return f'background-color: {st.get_option('theme.borderColor')}'


def color_users(val):
    if users.__contains__(val):
        return 'background-color: #ff4500; color: black; font-weight: bold;'

Colors = {
         'AVS': '#7adbff',
         'DRL': '#ffd7ff',
         'ETH': '#ffffcc',
         'EXP': '#ddebf7',
         'FAS': '#d5c4b9',
         'FLD': '#b8caa0',
         'LDR': '#ffc78f',
         'MED': '#fda69d',
         'NAV': '#fbe5fc',
         'OPS': '#90cbfc',
         'PHY': '#c9fbfa',
         'PMT': '#b7d2b4',
         'RCD': '#ffffff',
         'SAL': '#d8d8d8',
         'SEA': '#002060',
         'Other': "#949494"
         }

def color_lessons(val):
    try:
        if val.split()[0] in Colors:
            return f'background-color: {Colors[val.split()[0]]}; color: black;'
    except IndexError:
        pass
    

def get_training_program_names():        
    training_program_files = {}
    for file in st.session_state.SUPABASE_CONNECTION.training_programs:
        if file['path'] == 'active_training_programs.csv':
            active_training_programs = pd.read_csv(get_data(file))
    for file in st.session_state.SUPABASE_CONNECTION.training_programs:
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
tabs = st.tabs(['Training Program', 'Manager'])
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
            users = st.multiselect('Select Users to Display', options=[user['name'] for user in st.session_state.SUPABASE_CONNECTION.users.data], default=st.session_state.SUPABASE_CONNECTION.user['name'], help='Select the users to display.')

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

        rows_to_delete = []

        for start in range(2, len(df), 3):
            if start + 1 < len(df):
                for col in df.columns:
                    df.loc[start, col] = f'{df.loc[start, col]} {df.loc[start + 1, col]}'.removesuffix(' nan')
                    if df.loc[start, col] == 'nan':
                        df.loc[start, col] = ''
                rows_to_delete.append(start + 1)

        df = df.drop(index=rows_to_delete).reset_index(drop=True)


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
            st.dataframe(df.style.map(color_column, subset=[column]).map(color_users).map(color_lessons),
                        hide_index=True,
                        column_config=column_config,
                        height=705)
        except KeyError:
            st.dataframe(df,
                        hide_index=True,
                        height=705)
    except KeyError:
        st.error('No active training programs available')

with tabs[1]:
    if 'manage_training_program' in st.session_state.SUPABASE_CONNECTION.user['permissions_expanded']:
        columns = st.columns([2, 6, 1], gap='large')
        with columns[0]:
            for file in st.session_state.SUPABASE_CONNECTION.training_programs:
                if file['path'] == 'active_training_programs.csv':
                    active_TPs_df = pd.read_csv(get_data(file))
                    break
            st.write('##### Active Training Programs')
            edited_data = st.data_editor(active_TPs_df,
                                         column_config={
                                             'name': st.column_config.TextColumn('Name', width=125, disabled=True),
                                             'active': st.column_config.CheckboxColumn('Active', width=100)
                                         },
                                         hide_index=True,
                                         use_container_width=False,
                                         height=384)
            if (edited_data.to_dict(orient='records') != active_TPs_df.to_dict(orient='records')):
                csv_bytes = io.BytesIO(edited_data.to_csv(index=False).encode('utf-8'))
                csv_bytes.name = 'active_training_programs.csv'
                csv_bytes.type = 'text/csv'
                st.session_state.SUPABASE_CONNECTION.supabase.upload(bucket_id='training_programs',
                                            source='local',
                                            file=csv_bytes,
                                            destination_path='/active_training_programs.csv',
                                            overwrite='true')
                st.rerun()
        with columns[1]:
            st.write('##### Editor')
            all_training_programs = {}
            for file in st.session_state.SUPABASE_CONNECTION.training_programs:
                if file['path'] != 'active_training_programs.csv':
                    file_name = file['path']
                    file_name = file_name.removesuffix('.csv')
                    split_file_name = file_name.split('_')
                    year = split_file_name[0]
                    term = split_file_name[1]
                    file_renamed = f'{year}: Term {term}'
                    all_training_programs[file_renamed] = file
            selected_file = st.selectbox('Select Training Program', options=all_training_programs, help='Select the training program to edit.')
            if selected_file:
                df = pd.read_csv(get_data(all_training_programs[selected_file]))
                column_config = {}
                for week in df.columns:
                    column_config[week] = st.column_config.TextColumn(week, width=200)
                column_config['Year Group'] = st.column_config.TextColumn('Year Group', width=100, pinned=True)
                column_config['Period'] = st.column_config.TextColumn('Period', width=100, pinned=True)
                edited_data = st.data_editor(df,
                                column_config=column_config,
                                hide_index=True,
                                use_container_width=False,
                                height=300)
                sub_cols = st.columns([1, 1])
                with sub_cols[0]:
                    if st.button('**:green[Save Changes]**', help='Save changes to the training program', use_container_width=True):
                        csv_bytes = io.BytesIO(edited_data.to_csv(index=False).encode('utf-8'))
                        selected_file = selected_file.replace(': ', '_').replace('Term ', '')
                        csv_bytes.name = f'{selected_file}.csv'
                        csv_bytes.type = 'text/csv'
                        st.session_state.SUPABASE_CONNECTION.supabase.upload(bucket_id='training_programs',
                                                    source='local',
                                                    file=csv_bytes,
                                                    destination_path=f'/{csv_bytes.name}',
                                                    overwrite='true')
                        st.rerun()
                with sub_cols[1]:
                    if st.button('**:red[Remove Training Program]**', help='Remove the selected training program', use_container_width=True):
                        confirmation(selected_file)
            
    else:
        st.warning('You do not have permission to access this tab')