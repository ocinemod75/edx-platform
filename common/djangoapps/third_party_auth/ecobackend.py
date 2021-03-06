import base64
from social.backends.oauth import BaseOAuth2


class ECOOpenIdBackend(BaseOAuth2):
    """ECOOpendId authentication backend"""
    name = 'ecoopenid-auth'
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_METHOD = 'GET'
    DEFAULT_SCOPE = ['openid', 'profile', 'email']
    EXTRA_DATA = ['access_token', 'token_type', 'expires_in', 'id_token', 'refresh_token']

    @property
    def AUTHORIZATION_URL(self):
        return self.setting('IDP_URL') + "/authorize"  # 'http://ecoidp.test.reimeritsolutions.nl/authorize'

    @property
    def ACCESS_TOKEN_URL(self):
        return self.setting('IDP_URL') + "/token"  # 'http://ecoidp.test.reimeritsolutions.nl/token'

    @property
    def REVOKE_TOKEN_URL(self):
        return self.setting('IDP_URL') + "/token"  # 'http://ecoidp.test.reimeritsolutions.nl/token'

    @property
    def USERINFO_URL(self):
        return self.setting('IDP_URL') + "/userinfo"  # 'http://ecoidp.test.reimeritsolutions.nl/userinfo'

    def auth_headers(self):
        return {
            'Authorization': 'Basic {0}'.format(base64.urlsafe_b64encode(
                ('{0}:{1}'.format(*self.get_key_and_secret()).encode())
            ))
        }

    def get_user_details(self, response):
        """Return user details from ECO account"""
        email = response.get('email')
        return {'username': response.get('nickname'),
                'email': email,
                'fullname': response.get('name'),
                'first_name': response.get('given_name'),
                'last_name': response.get('family_name')}

    def get_user_id(self, details, response):
        """Use sub as unique id"""
        return response['sub']

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        values = self.get_json(self.USERINFO_URL,
                               headers={'Authorization': 'Bearer {0}'.format(access_token)}
                               )
        values['username'] = values['nickname']
        return values
