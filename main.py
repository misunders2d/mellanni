# -*- coding: utf-8 -*-
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import seaborn as sns
import yaml
from yaml import SafeLoader, SafeDumper
import matplotlib.pyplot as plt
st.set_page_config(page_title = 'M Tools App', page_icon = 'media/logo.ico',layout="wide")

import login
st.session_state['login'] = login.login()

if st.session_state['login']:
    st.write("logged in")

