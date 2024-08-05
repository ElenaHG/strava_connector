import os
import json
import requests
from requests.exceptions import RequestException
import webbrowser
from api_connector.authorization_error import AuthorizationError
import time
from datetime import datetime, timedelta

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs


class OAuth2Authenticator:

    REQUIRED_INITIAL_SECRET_KEYS = [
        'client_id', 'client_secret',
    ]

    SECRET_KEYS = REQUIRED_INITIAL_SECRET_KEYS + [        
        'code', 'access_token', 'refresh_token',
        'expires_at', 'expires_in', 'scope'
    ]

    CONNECTION_ATTRIBUTES = [
        'authorization_url',
        'token_url',
        'base_url'
    ]

    REDIRECT_URI = 'http://localhost:8080'

    def __init__(self,
                 connection_path: str,
                 secrets_path: str,
                 scope: str):
        if not os.path.exists(connection_path):
            raise ValueError('Please provide a valid connection path!')
        if not os.path.exists(secrets_path):
            raise ValueError('Please provide a valid secrets path!')
        self.connection_path = connection_path
        self.secrets_path = secrets_path

        # load connection attributes
        with open(connection_path, 'r') as file:
            self.connection = json.load(file)
        assert set(self.CONNECTION_ATTRIBUTES).issubset(self.connection.keys()), \
            f'Some required connection attributes are missing: {set(self.CONNECTION_ATTRIBUTES).difference(self.connection.keys())}'

        # load (initial) secrets
        with open(secrets_path, 'r') as file:
            self.secrets = json.load(file)
        assert set(self.REQUIRED_INITIAL_SECRET_KEYS).issubset(self.secrets.keys()), \
            f'Some required initial secret keys are missing: {set(self.REQUIRED_INITIAL_SECRET_KEYS).difference(self.secrets.keys())}'

        # set additional params
        self.scope = scope


    def authorize(self):
        # Correcting string formatting
        auth_url = (
            f"{self.connection['authorization_url']}?response_type=code"
            f"&client_id={self.secrets['client_id']}&redirect_uri={self.REDIRECT_URI}"
            f"&scope={' '.join(self.scope) if isinstance(self.scope, list) else self.scope}"
        )
        # Open the authorization URL in the default web browser
        webbrowser.open(auth_url)

        # Start the HTTP server
        with socketserver.TCPServer(('localhost', 8080), OAuth2Handler) as httpd:
            print('Listening for authorization code...')
            httpd.handle_request()
            code = httpd.auth_code
            if code:
                self.secrets['code'] = code
                self.scope = httpd.auth_scope
                self.get_initial_access_token(code)           
                print('Authorisation completed.')
            else:
                raise AuthorizationError('Authorization was not successful.')


    def get_initial_access_token(self, code):
        # Exchange the authorization code for an access token
        token_response = requests.post(
            self.connection['token_url'],
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.REDIRECT_URI,
                'client_id': self.secrets['client_id'],
                'client_secret': self.secrets['client_secret']
            }
        )
        self.handle_token_response(token_response)
    

    def refresh_access_token(self):
        token_response = requests.post(
            self.connection['token_url'],
            data={
                'grant_type': 'refresh_token',
                'client_id': self.secrets['client_id'],
                'client_secret': self.secrets['client_secret'],
                'refresh_token': self.secrets['refresh_token']
            }
        )
        self.handle_token_response(token_response)


    def get_access_token(self, buffer_time:int = 10):
        if ((not all(k in self.secrets.keys() for k in ['scope', 'expires_at', 'access_token'])) or 
            (self.scope not in self.secrets.get('scope'))):
            self.authorize() # do an (initial) authorization!
        else:
            # check if existing access_token is still valid by comparing expires_at timestamp with current time
            current_time = int(time.time())
            if self.secrets.get('expires_at') - current_time < buffer_time: # token expires too soon
                print("Reuse access_token as it is still valid")
                try:
                    self.refresh_access_token()
                except RequestException as e:
                    print(f'Using refresh token to get a new access token did not work: {e}')
                    self.authorize()
        return self.secrets.get('access_token')


    def handle_token_response(self, token_response: requests.Response):
        if token_response.ok:
            token_data = token_response.json()
            self.secrets.update(
                {k: v for k, v in token_data.items() if k in self.SECRET_KEYS}
            )
            self.secrets['scope'] = self.scope
            self.save_secrets()
        else:
            print(f'Error in token exchange: {token_response.status_code}, {token_response.text}')
            token_response.raise_for_status()
        

    def save_secrets(self):
        with open(self.secrets_path, 'w') as json_file:
            json.dump(self.secrets, json_file, indent=2)



class OAuth2Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Parse the URL query to extract the authorization code
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [None])[0]
        scope = query_components.get('scope', [None])[0]

        if code:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization code received. You can close this window.')

            # Store the code in the handler for access
            self.server.auth_code = code
            self.server.auth_scope = scope
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization code not found.')
        