import datetime
import logging
import time
from hashlib import md5
from collections import OrderedDict
import hmac
import json
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

import requests

from smartbridge.base.helpers import md5_string
from smartbridge.interfaces.exceptions import ProviderInternalException, ProviderConnectionException
from .devices import DeviceModels

log = logging.getLogger(__name__)


class WyzeClient(object):
    """
    Wyze client is the wrapper on top of Wyze endpoints
    """

    def __init__(self, config={}):
        self._config = config
        self._access_token = config.get('access_token')
        self._refresh_token = config.get('refresh_token')
        self._user_id = config.get('user_id')

        self._platform_client = None
        self._venus_client = None
        self._auth_client = None
        self._api_client = None
        self._general_api_client = None

        log.debug("wyze user : %s", self._user_id)

    @property
    def auth_client(self):
        if not self._auth_client:
            self._auth_client = WyzeAuthServiceClient(self._config)
        return self._auth_client

    @property
    def general_api_client(self):
        if not self._general_api_client:
            self._general_api_client = WyzeGeneralApiClient(
                self._config, self._access_token, self._user_id)
        return self._general_api_client

    @property
    def platform_client(self):
        if not self._platform_client:
            self._platform_client = WyzePlatformServiceClient(
                self._config, self._access_token)
        return self._platform_client

    @property
    def venus_client(self):
        if not self._venus_client:
            self._venus_client = WyzeVenusServiceClient(
                self._config, self._access_token)
        return self._venus_client

    @property
    def api_client(self):
        if not self._api_client:
            self._api_client = WyzeApiClient(self._config, self._access_token)
        return self._api_client

    def login(self, username, password):
        return self.auth_client.login(username, password)

    def refresh_token(self):
        return self.api_client.refresh_token()

    def list_devices(self):
        return self.api_client.get_object_list()['data']['device_list']

    def list_vacuums(self):
        return [device for device in self.list_devices(
        ) if device['product_model'] in DeviceModels.VACUUM]

    def get_vacuum(self, device_mac, props, device_info_props):
        vacuums = [_vacuum for _vacuum in self.list_vacuums()
                   if _vacuum['mac'] == device_mac]
        if len(vacuums) == 0:
            return None

        vacuum = vacuums[0]

        props = self.venus_client.get_iot_prop(device_mac, props)
        if (props and 'data' in props and props['data'] is not None):
            vacuum.update(props['data'])

        device_info_props = self.venus_client.get_device_info(
            device_mac, device_info_props)
        if (
                device_info_props and 'data' in device_info_props and device_info_props['data'] is not None):
            vacuum.update(device_info_props['data'])

        current_position = self.venus_client.get_current_position(device_mac)
        if (
                current_position and 'data' in current_position and current_position['data'] is not None):
            vacuum['current_position'] = current_position['data']

        current_map = self.venus_client.get_current_map(device_mac)
        if (
                current_map and 'data' in current_map and current_map['data'] is not None):
            vacuum['current_map'] = current_map['data']

        log.debug('returning vacuum data')
        log.debug(vacuum)

        return vacuum

    def set_vacuum_mode(self, device_mac, device_model, type, value):
        self.venus_client.set_iot_action(
            device_mac, device_model, 'set_mode', {
                'type': type, 'value': value})

    def set_vacuum_preference(
            self,
            device_mac,
            device_model,
            control_type,
            value):
        self.venus_client.set_iot_action(
            device_mac, device_model, 'set_preference', {
                'ctrltype': control_type, 'value': value})

    def create_user_vacuum_event(self, event_id, event_type):
        self._create_user_event(self.venus_client.app_id, event_id, event_type)

    def list_plugs(self):
        return [device for device in self.list_devices(
        ) if device['product_model'] in DeviceModels.PLUG]

    def get_plug(self, device_mac, props):
        plugs = [_plug for _plug in self.list_plugs() if _plug['mac']
                 == device_mac]
        if len(plugs) == 0:
            return None

        plug = plugs[0]
        plug.update(
            self.api_client.get_device_property_list(
                plug['mac'],
                plug['product_model'],
                props))

        log.debug('returning plug data')
        log.debug(plug)

        return plug

    def set_plug_property(self, device_mac, device_model, name, value):
        self.api_client.set_device_property(
            device_mac, device_model, name, value)

    def list_bulbs(self):
        return [device for device in self.list_devices(
        ) if device['product_model'] in DeviceModels.BULB]

    def get_bulb(self, device_mac, props):
        bulbs = [_bulb for _bulb in self.list_bulbs() if _bulb['mac']
                 == device_mac]
        if len(bulbs) == 0:
            return None

        bulb = bulbs[0]
        bulb.update(
            self.api_client.get_device_property_list(
                bulb['mac'],
                bulb['product_model'],
                props))

        log.debug('returning bulb data')
        log.debug(bulb)

        return bulb

    def set_bulb_property(self, device_mac, device_model, name, value):
        self.api_client.set_device_property(
            device_mac, device_model, name, value)

    def _create_user_event(self, pid, event_id, event_type):
        self.general_api_client.post_user_event(pid, event_id, event_type)


class WyzeServiceClient(object):
    """
    Wyze service client is the wrapper to Wyze service endpoints
    """
    __metaclass__ = ABCMeta

    def __init__(self, config, access_token=None):
        self._config = config
        self._access_token = access_token
        self._refresh_token = config.get('refresh_token')
        self._session = None

        log.debug("wyze service : %s", self.app_id)

    @property
    def app_name(self):
        return self._config.get('app_name')

    @property
    def app_ver(self):
        return self._config.get('app_ver')

    @property
    def app_version(self):
        return self._config.get('app_version')

    @abstractproperty
    def endpoint_url(self):
        pass

    @property
    def phone_id(self):
        return self._config.get('phone_id')

    @property
    def app_id(self):
        return self._config.get('app_id')

    def _do_request(
            self,
            session: requests.Session,
            request: requests.Request):
        try:
            log.trace('request')
            log.trace(request.headers)

            settings = session.merge_environment_settings(
                request.url, {}, None, None, None)

            log.debug(
                'sending ' +
                request.method +
                ' request to ' +
                request.url)
            response = session.send(request, **settings)

            log.trace('response')
            log.trace(response)

            response.raise_for_status()

            # Code here will only run if the request is successful
            response_json = response.json()

            log.trace('parsed response JSON')
            log.trace(response_json)

            if 'code' in response_json:
                response_code = response_json['code']

                if isinstance(response_code, int):
                    response_code = str(response_code)

                if response_code != '1' and 'msg' in response_json and response_json[
                        'msg'] == 'AccessTokenError':
                    log.warning(
                        "The user account is locked. Please resolve this issue and try again.")
                    raise ProviderConnectionException(
                        "Failed to login with response: {0}".format(response_json))
                if response_code != '1' and 'msg' in response_json and response_json[
                        'msg'] == "UserIsLocked":
                    log.warning(
                        "The user account is locked. Please resolve this issue and try again.")
                    raise ProviderConnectionException(
                        "Failed to login with response: {0}".format(response_json))
                if response_code != '1' and 'msg' in response_json and response_json[
                        'msg'] == "UserNameOrPasswordError":
                    log.warning(
                        "The username or password is incorrect. Please check your credentials and try again.")
                    raise ProviderConnectionException(
                        "Failed to login with response: {0}".format(response_json))
                if response_code == '1001':
                    log.error(
                        "Request to: {} does not respond to parameters in payload {} and gave a result of {}".format(
                            request.url, request.body, response_json))
                    raise ProviderInternalException(
                        "Parameters passed to Wyze Service do not fit the endpoint")
                if response_code == '1003':
                    # FIXME what do I mean?
                    log.error(
                        "Request to: {} does not respond to parameters in payload {} and gave a result of {}".format(
                            request.url, request.body, response_json))
                    raise ProviderInternalException(
                        "Parameters passed to Wyze Service do not fit the endpoint")
                if response_code == '1004':
                    log.error(
                        "Request to: {} does not have the correct signature2 of {} and gave a result of {}".format(
                            request.url, request.headers.signature2, response_json))
                    raise ProviderInternalException(
                        "Parameters passed to Wyze Service do not fit the endpoint")
                if response_code != '1':
                    print(type(response_code))
                    log.error(
                        "Request to: {} failed with payload: {} with result of {}".format(
                            request.url, request.body, response_json))
                    raise ProviderInternalException(
                        "Failed to connect to the Wyze Service")

            return response_json
        except requests.exceptions.RequestException as request_exception:
            log.exception(request_exception)
            raise ProviderConnectionException(request_exception)

    def do_post(self, url: str, headers: dict, payload: dict):
        with self.session as client:
            if headers is not None:
                # add the request-specific headers
                log.trace(
                    'merging request-specific headers into session headers')
                client.headers.update(headers)

            # we have to use a prepared request because the requests module
            # doesn't allow us to specify the separators in our json dumping
            # and the server expects no extra whitespace
            req = client.prepare_request(
                requests.Request(
                    'POST', url, json=payload))

            log.trace('unmodified prepared request')
            log.trace(req)

            if isinstance(payload, dict):
                payload = json.dumps(payload, separators=(',', ':'))
            if isinstance(payload, str):
                req.body = payload.encode('utf-8')
                req.prepare_content_length(req.body)

            return self._do_request(client, req)

    def do_get(self, url: str, headers: dict, payload: dict):
        with self.session as client:
            if headers is not None:
                # add the request-specific headers
                log.trace(
                    'merging request-specific headers into session headers')
                client.headers.update(headers)

            req = client.prepare_request(
                requests.Request(
                    'GET', url, params=payload))

            return self._do_request(client, req)

    def _nonce(self):
        return str(round(time.time() * 1000))


class WyzeWpkNetServiceClient(WyzeServiceClient):
    """
    Wyze wpk net service client is the wrapper to newer Wyze services like WpkWyzeSignatureService and WpkWyzeExService
    """
    __metaclass__ = ABCMeta

    SALTS = {
        "9319141212m2ik": "wyze_app_secret_key_132",
        "venp_4c30f812828de875": "CVCSNoa0ALsNEpgKls6ybVTVOmGzFoiq",
    }

    def __init__(self, config, access_token=None):
        super(WyzeWpkNetServiceClient, self).__init__(config, access_token)

    @abstractproperty
    def session(self):
        """
        Returns the provider instance associated with this resource.
        Intended for use by subclasses only.
        :rtype: :class:`.CloudProvider`
        :return: a CloudProvider object
        """
        pass

    def get_from_server(self, url, payload={}):
        # create the time-based nonce and add it to the payload
        nonce = self._nonce()

        # this must be done here so that it will be included in the signing
        payload['nonce'] = nonce

        headers = {
            'access_token': self._access_token,
            'requestid': self.request_id(nonce),
            'signature2': self.dynamic_signature(
                self.get_sorted_params(
                    sorted(
                        payload.items()))),
        }
        return self.do_get(url, headers, payload)

    def post_to_server(self, url, payload={}):
        # create the time-based nonce and add it to the payload
        nonce = self._nonce()

        # this must be done here so that it will be included in the signing
        payload['nonce'] = nonce

        request_data = json.dumps(payload, separators=(',', ':'))

        headers = {
            'access_token': self._access_token,
            'requestid': self.request_id(nonce),
            'signature2': self.dynamic_signature(request_data)
        }

        return self.do_post(url, headers, request_data)

    def get_sorted_params(self, params):
        return '&'.join(map(lambda x: x[0] + '=' + x[1], params))

    def request_id(self, nonce=None):
        if nonce is None:
            nonce = self._nonce()
        return md5_string(md5_string(nonce))

    def dynamic_signature(self, message=''):
        _signing_key = md5_string(
            (self._access_token if self._access_token is not None else '') + WyzeWpkNetServiceClient.SALTS[self.app_id])

        return hmac.new(
            _signing_key.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=md5).hexdigest()


class WyzeExServiceClient(WyzeWpkNetServiceClient):
    """
    Wyze ex service client is the wrapper for WpkWyzeExService
    """
    __metaclass__ = ABCMeta

    def __init__(self, config, access_token=None):
        super(WyzeExServiceClient, self).__init__(config, access_token)


class WyzeSignatureServiceClient(WyzeWpkNetServiceClient):
    """
    Wyze signature service client is the wrapper for WpkWyzeSignatureService
    """
    __metaclass__ = ABCMeta

    def __init__(self, config, access_token):
        super(WyzeSignatureServiceClient, self).__init__(config, access_token)


class WyzeVenusServiceClient(WyzeSignatureServiceClient):

    def __init__(self, config, access_token):
        super(WyzeVenusServiceClient, self).__init__(config, access_token)

    def __eq__(self, other):
        return (isinstance(other, WyzeVenusServiceClient) and
                # pylint:disable=protected-access
                self.app_id == other.app_id)

    @property
    def app_id(self):
        return 'venp_4c30f812828de875'

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.7.2',
                'appid': self.app_id,
                'appinfo': 'wyze_android_2.16.55',
                'phoneid': self.phone_id,
            })

        return self._session

    @property
    def endpoint_url(self):
        return 'https://wyze-venus-service-vn.wyzecam.com'

    def get_current_position(self, did):
        return self.get_from_server(
            self.endpoint_url +
            '/plugin/venus/memory_map/current_position',
            payload={
                'did': did,
            })

    def get_current_map(self, did):
        return self.get_from_server(
            self.endpoint_url +
            '/plugin/venus/memory_map/current_map',
            payload={
                'did': did,
            })

    def get_sweep_records(self, did, keys):
        return self.get_from_server(
            self.endpoint_url +
            '/plugin/venus/sweep_record/query_data',
            payload={
                'purpose': 'history_map',
                'last_time': 1614006488650,
                'count': 20,
                'did': did,
                'keys': ','.join(keys),
            })

    def get_iot_prop(self, did, keys):
        return self.get_from_server(
            self.endpoint_url +
            '/plugin/venus/get_iot_prop',
            payload={
                'did': did,
                'keys': ','.join(keys),
            })

    def get_device_info(self, did, keys):
        return self.get_from_server(
            self.endpoint_url +
            '/plugin/venus/device_info',
            payload={
                'device_id': did,
                'keys': ','.join(keys),
            })

    def set_iot_action(self, did, model, cmd, params, is_sub_device=False):
        return self.post_to_server(
            self.endpoint_url +
            '/plugin/venus/set_iot_action',
            payload={
                'cmd': cmd,
                'did': did,
                'model': model,
                'is_sub_device': is_sub_device,
                'params': params,
            })


class WyzePlatformServiceClient(WyzeExServiceClient):

    def __init__(self, config, access_token):
        super(WyzePlatformServiceClient, self).__init__(config, access_token)

    def __eq__(self, other):
        return (isinstance(other, WyzePlatformServiceClient) and
                # pylint:disable=protected-access
                self.app_id == other.app_id)

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.7.2',
                'appid': self.app_id,
                'appinfo': 'wyze_android_2.16.55',
                'phoneid': self.phone_id,
            })

        return self._session

    @property
    def endpoint_url(self):
        return 'https://wyze-platform-service.wyzecam.com'

    def get_variable(self, keys):
        return self.get_from_server(
            self.endpoint_url +
            '/app/v2/platform/get_variable',
            payload={
                'keys': ','.join(keys),
                'category': 'app',
            })

    def get_user_profile(self):
        return self.get_from_server(
            self.endpoint_url +
            '/app/v2/platform/get_user_profile')


class WyzeAuthServiceClient(WyzeExServiceClient):

    X_API_KEY = 'RckMFKbsds5p6QY3COEXc2ABwNTYY0q18ziEiSEm'

    def __init__(self, config={}):
        super(WyzeAuthServiceClient, self).__init__(config)

    def __eq__(self, other):
        return (isinstance(other, WyzeAuthServiceClient) and
                # pylint:disable=protected-access
                self.app_id == other.app_id)

    @property
    def endpoint_url(self):
        return 'https://auth-prod.api.wyze.com'

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                'accept-encoding': 'gzip',
                'phone-id': self.phone_id,
                'x-api-key': WyzeAuthServiceClient.X_API_KEY,
                'user-agent': 'wyze_android_2.16.55',
                'appinfo': 'wyze_android_2.16.55',
                'appid': self.app_id,
            })

        return self._session

    def login(self, email='', password=''):
        _nonce = self._nonce()

        payload = {
            'nonce': _nonce,
            'email': email,
            'password': md5_string(md5_string(md5_string(password)))
        }

        with self.session as client:
            client.headers.update({
                'requestid': self.request_id(),
                'signature2': self.dynamic_signature(json.dumps(payload, separators=(',', ':')))
            })

            return self.do_post(
                self.endpoint_url +
                '/user/login',
                None,
                payload)


class WyzeGeneralApiClient(WyzeServiceClient):
    """
    Wyze api client is the wrapper on the requests to https://wyze-general-api.wyzecam.com
    """

    def __init__(self, config, access_token, user_id):
        super(WyzeGeneralApiClient, self).__init__(config, access_token)
        self._user_id = user_id

    def __eq__(self, other):
        return (isinstance(other, WyzeGeneralApiClient) and
                # pylint:disable=protected-access
                self.app_id == other.app_id)

    @property
    def sdk_version(self):
        return '1.2.3'

    @property
    def sdk_type(self):
        return '100'

    @property
    def endpoint_url(self):
        return 'https://wyze-general-api.wyzecam.com'

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.7.2',
                'wyzesdktype': self.sdk_type,
                'wyzesdkversion': self.sdk_version,
            })

        return self._session

    def post_to_server(self, url, api_key, payload={}):
        with self.session as client:

            payload['apiKey'] = api_key
            payload['appId'] = self.app_id
            payload['appVersion'] = self.app_version
            payload['deviceId'] = self.phone_id

            return self.do_post(url, None, payload)

    def post_user_event(self, pid, event_id, event_type):
        # create the time-based nonce and add it to the payload
        nonce = self._nonce()

        payload = {
            'eventId': event_id,
            'eventType': event_type,
            'logSdk': 100,
            'logTime': int(nonce),
            'nonce': nonce,
            'osInfo': 'Android',
            'osVersion': '9',
            'pid': pid,
            'uid': self._user_id,
        }

        return self.post_to_server(
            self.endpoint_url + '/v1/user/event', '', payload)


class WyzeApiClient(WyzeServiceClient):
    """
    Wyze api client is the wrapper on the requests to https://api.wyzecam.com
    """

    SC = 'a626948714654991afd3c0dbd7cdb901'

    def __init__(self, config, access_token):
        super(WyzeApiClient, self).__init__(config, access_token)

    def __eq__(self, other):
        return (isinstance(other, WyzeApiClient) and
                # pylint:disable=protected-access
                self.app_id == other.app_id)

    @property
    def app_name(self):
        return 'com.hualai'

    @property
    def app_ver(self):
        return self.app_name + '___' + self.app_version

    @property
    def endpoint_url(self):
        return 'https://api.wyzecam.com'

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.7.2',
                'connection': 'keep-alive',
            })

        return self._session

    def post_to_server(self, url, payload={}):
        with self.session as client:
            payload['access_token'] = self._access_token
            payload['app_name'] = self.app_name
            payload['app_ver'] = self.app_ver
            payload['app_version'] = self.app_version
            payload['phone_id'] = self.phone_id
            payload['sc'] = WyzeApiClient.SC
            # create the time-based nonce and add it to the payload
            payload['ts'] = str(int(time.time()))
            return self.do_post(url, None, payload)

    def refresh_token(self):
        SV_REFRESH_TOKEN = 'd91914dd28b7492ab9dd17f7707d35a3'

        return self.post_to_server(
            self.endpoint_url +
            '/app/user/refresh_token',
            {
                'refresh_token': self._refresh_token,
                'sv': SV_REFRESH_TOKEN})

    def set_device_property(self, mac, model, pid, value):
        SV_SET_DEVICE_PROPERTY = '44b6d5640c4d4978baba65c8ab9a6d6e'

        return self.post_to_server(
            self.endpoint_url +
            '/app/v2/device/set_property',
            {
                'device_mac': mac,
                'device_model': model,
                'pid': pid,
                'pvalue': str(value),
                'sv': SV_SET_DEVICE_PROPERTY})

    def get_device_list_property_list(self, devices=[], target_pids=[]):
        SV_GET_DEVICE_LIST_PROPERTY_LIST = 'be9e90755d3445d0a4a583c8314972b6'

        return self.post_to_server(
            self.endpoint_url +
            '/app/v2/device_list/get_property_list',
            {
                'device_list': devices,
                'target_pid_list': target_pids,
                'sv': SV_GET_DEVICE_LIST_PROPERTY_LIST})

    def get_device_property_list(self, mac, model, target_pids=[]):
        SV_GET_DEVICE_PROPERTY_LIST = '1df2807c63254e16a06213323fe8dec8'

        return self.post_to_server(
            self.endpoint_url +
            '/app/v2/device/get_property_list',
            {
                'device_mac': mac,
                'device_model': model,
                'target_pid_list': target_pids,
                'sv': SV_GET_DEVICE_PROPERTY_LIST})

    def get_object_list(self):
        SV_GET_DEVICE_LIST = 'c417b62d72ee44bf933054bdca183e77'

        return self.post_to_server(
            self.endpoint_url + '/app/v2/home_page/get_object_list', {'sv': SV_GET_DEVICE_LIST})
