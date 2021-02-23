import os
import unittest
import logging
import smartbridge
from smartbridge.factory import ProviderFactory, ProviderList
import uuid


class TestLogin(unittest.TestCase):
    def test_login(self):
        client_cfg = {
            'wyze_app_id': '9319141212m2ik',
            'wyze_app_name': 'wyze',
            'wyze_app_version': '2.16.55',
            'wyze_phone_id': str(uuid.uuid4()),
        }
        smartbridge.set_stream_logger('smartbridge', logging.DEBUG)
        login_response = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg).wyze_client.login(
            os.getenv('WYZE_USERNAME'), os.getenv('WYZE_PASSWORD'))

        client_cfg['access_token'] = login_response['access_token']
        client_cfg['refresh_token'] = login_response['refresh_token']
        client_cfg['user_id'] = login_response['user_id']

        provider = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg)
        self.assertIsNotNone(provider)


if __name__ == '__main__':
    unittest.main()
