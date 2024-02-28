import os
import json
import webbrowser
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import streamlit as st


# These URI should match the Authorized redirect URIs in
# Google Cloud Credentials
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8501/')
CLIENT_ID = os.environ.get('CLIENT_ID', '430995157603-4m4081s2jv7skkpn7evd01qap0pj6vs5.apps.googleusercontent.com')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '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')
PROJECT_ID = os.environ.get('PROJECT_ID', 'transcribe-392421')


def authenticate():
    """Authenticate using Google as the IDP provider."""

    st.write('Google Auth with Streamlit!')
    auth_code = st.query_params.get('code')

    # This string should look exactly the same as the secrets file from GCP
    json_str = '{'\
               '"web":'\
               '{'\
               f'   "client_id":"{CLIENT_ID}",'\
               f'   "project_id":"{PROJECT_ID}",'\
               '   "auth_uri":"https://accounts.google.com/o/oauth2/auth",'\
               '   "token_uri":"https://oauth2.googleapis.com/token",'\
               '   "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",'\
               f'   "client_secret":"{CLIENT_SECRET}",'\
               f'   "redirect_uris":["{REDIRECT_URI}"],'\
               f'   "javascript_origins":["{REDIRECT_URI}"]'\
               '}'\
               '}'

    client_config = json.loads(json_str)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config,
            scopes=[
                'https://www.googleapis.com/auth/userinfo.email',
                'openid'],
            redirect_uri=REDIRECT_URI,
        )

    if auth_code:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        st.write('Login Successful!')
        user_info_service = build(
            serviceName='oauth2',
            version='v2',
            credentials=credentials,
        )
        user_info = user_info_service.userinfo().get().execute()
        assert user_info.get('email'), 'Email not found in user info'
        st.session_state['google_auth_code'] = auth_code
        st.session_state['user_info'] = user_info
    else:
        if st.button('Authenticate with Google'):
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
            )
            webbrowser.open_new_tab(authorization_url)


def main():
    """Main method"""
    if 'google_auth_code' not in st.session_state:
        authenticate()

    if "google_auth_code" in st.session_state:
        email = st.session_state["user_info"].get("email")
        image_link = st.session_state["user_info"].get("picture")
        st.write(f"Hi {email}")
        st.image(image_link, width=50)


if __name__ == "__main__":
    main()
