from time import time
from urllib.parse import urlparse, parse_qs

import requests


class Authenticator:
    URLS = {
        'BASE_URI': 'https://ca.account.sony.com/api',
        'CLIENT_ID': 'ac8d161a-d966-4728-b0ea-ffec22f69edc',
        'SCOPE': 'psn:clientapp psn:mobile.v1',
        'REDIRECT_URI': 'com.playstation.PlayStationApp://redirect'
    }

    # constructor
    def __init__(self, npsso_token):
        """
        To get 64 character npsso code refer to the README.md

        :param npsso_token:
        """
        self.npsso_token = npsso_token
        self.oauth_token_response = None
        self.access_token_expiration = None
        self.refresh_token_expiration = None
        self.authenticate()

    def obtain_fresh_access_token(self):
        """
        Gets a new access token from refresh token

        :return: str: access token
        """
        data = {'refresh_token': self.oauth_token_response['refresh_token'],
                'grant_type': 'refresh_token', 'scope': Authenticator.URLS['SCOPE'], 'token_format': 'jwt'}
        auth_header = {'Authorization': 'Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY='
                       }
        response = requests.post(url='{}/authz/v3/oauth/token'.format(Authenticator.URLS['BASE_URI']),
                                 headers=auth_header,
                                 data=data)
        self.oauth_token_response = response.json()
        self.access_token_expiration = time() + self.oauth_token_response['expires_in']
        self.refresh_token_expiration = time() + self.oauth_token_response['refresh_token_expires_in']
        return self.oauth_token_response['access_token']

    # returns the access code
    def get_access_token(self):
        """
        Gets the access token value

        :return: str: access token value
        """
        return self.oauth_token_response['access_token']

    # Tells how much times remain till access token expires
    def access_token_expires_in(self):
        """
        Checks how much time is remaining till expiration

        :returns: float: time remaining in seconds
        """
        return time() - self.access_token_expiration

    # Tells if access token has expired
    def is_access_token_expired(self):
        """
        Checks if the access token is expired

        :returns: Boolean
        """
        return time() >= self.access_token_expiration

    # Tells how much times remain till access refresh expires
    def refresh_token_expires_in(self):
        """
        Checks how much time is remaining till expiration

        :returns: float: time remaining in seconds
        """
        return time() - self.refresh_token_expiration

    # Tells if refresh token has expired
    def is_refresh_token_expired(self):
        """
        Checks if the access token is expired

        :returns: Boolean
        """
        return time() >= self.refresh_token_expiration

    # Obtain oauth token if the code is passed otherwise refreshes the access token using refresh token
    def oauth_token(self, code):
        """
        Internal Function, Do not call directly.

        :param code: Code obtained using npsso code
        """

        data = {'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': Authenticator.URLS['REDIRECT_URI'],
                'scope': Authenticator.URLS['SCOPE'],
                'token_format': 'jwt'}

        auth_header = {'Authorization': 'Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY='
                       }

        response = requests.post(url='{}/authz/v3/oauth/token'.format(Authenticator.URLS['BASE_URI']),
                                 headers=auth_header,
                                 data=data)
        self.oauth_token_response = response.json()
        self.access_token_expiration = time() + self.oauth_token_response['expires_in']
        self.refresh_token_expiration = time() + self.oauth_token_response['refresh_token_expires_in']

    # Authenticate using npsso
    def authenticate(self):
        """
        Authenticate using the npsso code provided in the constructor

        Obtains the access code and the refresh code. Access code lasts about 1 hour. While the refresh code lasts
        about 2 months. After 2 months a new npsso code is needed.

        :raises ValueError:
        """
        cookies = {'Cookie': 'npsso=' + self.npsso_token}
        params = {'access_type': 'offline',
                  'client_id': Authenticator.URLS['CLIENT_ID'],
                  'scope': Authenticator.URLS['SCOPE'],
                  'redirect_uri': Authenticator.URLS['REDIRECT_URI'],
                  'response_type': 'code'}
        response = requests.get(url='{}/authz/v3/oauth/authorize'.format(Authenticator.URLS['BASE_URI']),
                                headers=cookies,
                                params=params, allow_redirects=False)
        location_url = response.headers['location']
        parsed_url = urlparse(location_url)
        parsed_query = parse_qs(parsed_url.query)
        self.oauth_token(parsed_query['code'][0])
