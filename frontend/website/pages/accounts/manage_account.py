import streamlit as st

cols = st.columns([1, 20], vertical_alignment='bottom')
with cols[0]:
    st.image(st.experimental_user['picture'])
with cols[1]:
    st.write(f'### Welcome *{st.experimental_user['given_name']}*')
st.write(f'**Full Name:** {st.experimental_user['name']}')
st.write(f'**Email:** {st.experimental_user['email']}')
if st.button('Log out'):
    st.logout()