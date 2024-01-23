import streamlit as st
from streamlit_oauth import OAuth2Component

# Set environment variables
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"
CLIENT_ID = st.secrets['GCLIENT_ID']
CLIENT_SECRET = st.secrets['GCLIENT_SECRET']
REDIRECT_URI = "http://localhost:8501"
SCOPE = "openid profile email"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

def login_google():
    # Check if token exists in session state
    if 'token' not in st.session_state:
        # If not, show authorize button
        result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
        if result and 'token' in result:
            # If authorization successful, save token in session state
            st.session_state.token = result.get('token')
            # THE MAIN APP if user authenticate
            st.title("App On")
            
    else:
        token = st.session_state['token']

    return token