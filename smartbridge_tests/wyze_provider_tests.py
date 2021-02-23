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
        smartbridge.set_stream_logger('smartbridge', logging.WARN)
        login_response = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg).wyze_client.login(
            os.getenv('WYZE_USERNAME'), os.getenv('WYZE_PASSWORD'))

        client_cfg['access_token'] = login_response['access_token']
        client_cfg['refresh_token'] = login_response['refresh_token']
        client_cfg['user_id'] = login_response['user_id']

        provider = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg)
        self.assertIsNotNone(provider)


class TestBulb(unittest.TestCase):
    def setUp(self):
        # Login and create the provider
        client_cfg = {
            'wyze_app_id': '9319141212m2ik',
            'wyze_app_name': 'wyze',
            'wyze_app_version': '2.16.55',
            'wyze_phone_id': str(uuid.uuid4()),
        }
        smartbridge.set_stream_logger('smartbridge', logging.WARN)
        login_response = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg).wyze_client.login(
            os.getenv('WYZE_USERNAME'), os.getenv('WYZE_PASSWORD'))

        client_cfg['access_token'] = login_response['access_token']
        client_cfg['refresh_token'] = login_response['refresh_token']
        client_cfg['user_id'] = login_response['user_id']

        self.provider = ProviderFactory().create_provider(ProviderList.WYZE, client_cfg)

    def test_list_bulbs(self):
        bulbs = self.provider.bulb.list()
        self.assertGreaterEqual(len(bulbs), 1)

    def test_bulb_off(self):
        bulb = self.provider.bulb.get(os.getenv('TEST_BULB_MAC'))
        bulb.switch_off()

    def test_bulb_on(self):
        bulb = self.provider.bulb.get(os.getenv('TEST_BULB_MAC'))
        bulb.switch_on()

    def test_bulb_brightness(self):
        bulb = self.provider.bulb.get(os.getenv('TEST_BULB_MAC'))
        bulb.brightness = 100

    def test_bulb_color_temp(self):
        bulb = self.provider.bulb.get(os.getenv('TEST_BULB_MAC'))
        bulb.color_temp = 2700


if __name__ == '__main__':
    unittest.main()
