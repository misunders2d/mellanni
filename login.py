import streamlit as st
import streamlit_google_oauth as oauth

def login():
    login_info = oauth.login(
            client_id=st.secrets['GCLIENT_ID'],
            client_secret=st.secrets['GCLIENT_SECRET'],
            # redirect_uri = 'localhost'
            # redirect_uri='https://mellanni-tools.streamlit.app/main',
            # login_button_text="Continue with Google",
            # logout_button_text="Logout",
        )

    if login_info:
            user_id, user_email = login_info
            st.write(f"Welcome {user_email}")
            st.write(login_info)
            return login_info
    else:
            st.write("Please login")
            return (None,None,None)
    
if __name__ == '__main__':
       st.write(login())
