# -*- coding: utf-8 -*-
import streamlit as st
import streamlit_authenticator as stauth
st.set_page_config(page_title = 'M Tools App', page_icon = 'media/logo.ico',layout="wide")

import login
st.session_state['login'], st.session_state['name'] = login.login()

if st.session_state['login']:
    st.write("logged in")

