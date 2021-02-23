"""Provider implementation based on wyze.com ReSTful API."""
import logging
import uuid

import requests

from smartbridge.base import BaseProvider
from smartbridge.base.helpers import get_env

from .client import WyzeClient

from .services import WyzeBulbService
from .services import WyzePlugService
from .services import WyzeVacuumService

log = logging.getLogger(__name__)


class WyzeProvider(BaseProvider):
    '''wyze.com provider interface'''
    PROVIDER_ID = 'wyze'

    def __init__(self, config):
        super(WyzeProvider, self).__init__(config)

        self.access_token = self._get_config_value('access_token', None)
        self.refresh_token = self._get_config_value('refresh_token', None)
        self.user_id = self._get_config_value('user_id', None)

        # Initialize connection fields
        self.app_id = self._get_config_value('wyze_app_id', '9319141212m2ik')
        self.app_name = self._get_config_value('wyze_app_name', 'wyze')
        self.app_version = self._get_config_value(
            'wyze_app_version', '2.16.55')

        self.phone_id = self._get_config_value(
            'wyze_phone_id', str(uuid.uuid4()))
        self.phone_system_type = self._get_config_value(
            'wyze_phone_system_type', 2)

        self.session_cfg = {
            'wyze_username': self._get_config_value(
                'wyze_username',
                get_env('WYZE_USERNAME')),
            'wyze_password': self._get_config_value(
                'wyze_password',
                get_env('WYZE_PASSWORD')),
            'wyze_access_token': self._get_config_value(
                'wyze_access_token',
                None)}

        self.client_cfg = {
            'use_ssl': self._get_config_value('wyze_is_secure', True),
            'verify': self._get_config_value('wyze_validate_certs', True)
        }

        # service connections, lazily initialized
        self._session = None
        self._wyze_client = None

        # Initialize provider services
        self._bulb = WyzeBulbService(self)
        self._plug = WyzePlugService(self)
        self._vacuum = WyzeVacuumService(self)

    @property
    def wyze_client(self):
        if not self._wyze_client:
            # create a dict with both optional and mandatory configuration
            # values to pass to the client class, rather
            # than passing the provider object and taking a dependency.
            provider_config = {
                'app_id': self.app_id,
                'app_name': self.app_name,
                'app_version': self.app_version,
                'phone_id': self.phone_id,
                'phone_system_type': self.phone_system_type,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'user_id': self.user_id,
            }
            self._wyze_client = WyzeClient(provider_config)

        return self._wyze_client

    @property
    def session(self):
        '''Get a low-level session object or create one if needed'''
        if not self._session:
            if self.config.debug_mode:
                requests.set_stream_logger(level=log.DEBUG)
            self._session = requests.Session()

        return self._session

    @property
    def plug(self):
        return self._plug

    @property
    def vacuum(self):
        return self._vacuum

    @property
    def bulb(self):
        return self._bulb
