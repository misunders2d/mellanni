import streamlit as st

import login
st.session_state['login'], st.session_state['name'] = login.login()

if st.session_state['login']:
    st.write('Success')