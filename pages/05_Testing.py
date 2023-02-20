import streamlit as st
import streamlit_authenticator as stauth
from deta import Deta

db_token = st.secrets['DB_USERS']
deta = Deta(db_token)
base = deta.Base('mellanni_users')
results = base.fetch().items
st.write(results)

# authenticator = stauth.authenticate(names,usernames,hashed_passwords,'cookie_name', 'signature_key',cookie_expiry_days=30)


# if 'registered' in st.session_state:
#     authenticator = stauth.Authenticate(
#         st.session_state.config['credentials'],
#         st.session_state.config['cookie']['name'],
#         st.session_state.config['cookie']['key'],
#         st.session_state.config['cookie']['expiry_days'],
#         st.session_state.config['preauthorized']
#     )
#     st.write(st.session_state.config['credentials'])
#     name, authentication_status, username = authenticator.login('Login', 'main')
#     if authentication_status:
#         authenticator.logout('Logout', 'main')
#         st.write(f'Welcome *{name}*')
#         st.title('Some content')
#     elif authentication_status is False:
#         st.error('Username/password is incorrect')
#     elif authentication_status is None:
#         st.warning('Please enter your username and password')    

# else:
#     col1,col2,col3 = st.columns([1,2,1])
#     if col3.button('Sign Up') or 'signup' in st.session_state:
#         st.session_state.signup = True
#         name = col3.text_input('user name')
#         email = col3.text_input('email')
#         pwd = col3.text_input('password', type = 'password')
#         col3.button('Submit', on_click=submit)
        



