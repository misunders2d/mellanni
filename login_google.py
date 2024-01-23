import streamlit as st
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.oauth2 import id_token

# # Set your Google client ID and secret
# CLIENT_ID = '60688562422-lmivhsa8qprhi34u70bt5vgn6qdedrub.apps.googleusercontent.com'
# CLIENT_SECRET = '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'
# REDIRECT_URI = 'https://www.google.com/'  # Must match the one configured in the Google Cloud Console
# CLIENT_FILE = r'G:\Shared drives\70 Data & Technology\70.03 Scripts\mellanni_2\google-cloud\mellanni_login.json'

# def login_with_google():
#     st.subheader("Login with Google")

#     flow = InstalledAppFlow.from_client_secrets_file(
#         CLIENT_FILE,  # Download this file from Google Cloud Console
#         scopes=['openid', 'email', 'profile'],
#         redirect_uri=REDIRECT_URI
#     )

#     auth_url, _ = flow.authorization_url(prompt='consent')

#     # Redirect user to Google for authentication
#     st.markdown(f"[Sign in with Google]({auth_url})", unsafe_allow_html=True)

#     # Get the authorization response from the user
#     auth_response = st.text_input("Paste the full redirect URL here:")

#     if auth_response and st.button("Submit"):
#         flow.fetch_token(authorization_response=auth_response)

#         # Get user information from the ID token
#         id_info = id_token.verify_oauth2_token(
#             flow.credentials.id_token, Request(), CLIENT_ID
#         )

#         st.success(f"Successfully authenticated as {id_info['email']}")

# def main():
#     st.title("Streamlit Google Authentication Example")

#     if not st.session_state.get("authenticated", False):
#         login_with_google()
#         st.stop()

#     st.success("You are authenticated!")

# if __name__ == "__main__":
#     main()



import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Replace with your Google OAuth client ID and secret
CLIENT_ID = '60688562422-lmivhsa8qprhi34u70bt5vgn6qdedrub.apps.googleusercontent.com'
CLIENT_SECRET = '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'
CLIENT_FILE = r'G:\Shared drives\70 Data & Technology\70.03 Scripts\mellanni_2\google-cloud\mellanni_login.json'

# Define the redirect URI for your Streamlit app
REDIRECT_URI = "http://localhost:8501/callback/"

# Create the OAuth flow
flow = Flow.from_client_secrets_file(
    CLIENT_FILE, scopes=["profile", "email"], redirect_uri=REDIRECT_URI
)

# Create the login button
login_button = st.button("Login with Google")

# Handle login flow
if login_button:
    authorization_url, state = flow.authorization_url()
    st.markdown(f"<a href='{authorization_url}'>Login with Google</a>", unsafe_allow_html=True)

    # # Get the authorization code from the redirect URI
    # if "code" in st.query_string:
    #     code = st.query_string["code"]
    #     flow.fetch_token(code=code, client_secret=CLIENT_SECRET)

    #     # Get user information from Google
    #     response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {flow.token.access_token}"})
    #     user_info = response.json()

    #     st.write(f"Welcome, {user_info['name']}!")
    #     # You can access user information like email, profile picture, etc. from user_info dictionary
