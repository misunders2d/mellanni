# -*- coding: utf-8 -*-
import streamlit as st
import streamlit_authenticator as stauth
import streamlit_google_oauth as oauth
st.set_page_config(page_title = 'Mellanni Tools App', page_icon = 'media/logo.ico',layout="wide")

import login
st.session_state['login'] = login.login()
st.write(st.session_state['login'])

if st.session_state['login']:
    st.write("logged in")
