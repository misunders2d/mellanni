import streamlit as st
import streamlit_authenticator as stauth
from deta import Deta

def login():
    preauthorized_emails = [
        'sergey@mellanni.com','sergey@poluco.co','oleksandr@mellanni.com','yuri@mellanni.com','dima@mellanni.com','ruslan@mellanni.com',
        'olha@mellanni.com'
        ]

    if 'base' not in st.session_state:
        db_token = st.secrets['DB_USERS']
        deta = Deta(db_token)
        # deta = Deta('a0bc7xb753v_mcmdiBnc2rm6G9341fPNW4uV5S3cqg2x')
        base = deta.Base('mellanni_users')
        results = base.fetch().items
        names = [x['name'] for x in results]
        usernames =[x['key'] for x in results]
        passwords = [x['password'] for x in results]
        credentials = {"usernames":{}}

        for un, name, pw in zip(usernames, names, passwords):
            user_dict = {"name":name,"password":pw}
            credentials["usernames"].update({un:user_dict})    
                    
        st.session_state['credentials'] = credentials
        st.session_state['base'] = base

    authenticator = stauth.Authenticate(
        st.session_state['credentials'],
        'mellanni_access',
        'cookie_for_mellanni',
        cookie_expiry_days=30,
        preauthorized={'emails':preauthorized_emails})
    user, authentication_status, name = authenticator.login('Login','main')
    if not st.session_state['authentication_status']:
        st.write('OR')

        with st.form('Register'):
            name = st.text_input("What's your name?")
            username = st.text_input('Create a username')
            email = st.text_input('Input user email')
            password_str = st.text_input('Input user password', type = 'password')
            if st.form_submit_button('Submit'):
                password = stauth.Hasher([password_str]).generate()[0]
                user = {'key':username,'name':name,'email':email,'password':password}
                if email in preauthorized_emails:
                    if st.session_state['base'].insert(user):
                        st.success('Successfully registered')
                else:
                    st.warning('This user is not allowed to register')


    if st.session_state['authentication_status']:
        authenticator.logout('Logout', 'sidebar')
    elif st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] == None:
        st.warning('Please enter your username and password')

    return st.session_state['authentication_status']