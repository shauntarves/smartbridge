"""Base implementation of a provider interface."""
import functools
import logging
import os
from os.path import expanduser
from configparser import ConfigParser

from ..interfaces import Provider
from ..interfaces.exceptions import ProviderConnectionException
from ..interfaces.devices import Configuration

log = logging.getLogger(__name__)

DEFAULT_RESULT_LIMIT = 50
DEFAULT_WAIT_TIMEOUT = 600
DEFAULT_WAIT_INTERVAL = 5

# By default, use two locations for Smartbridge configuration
SmartbridgeConfigPath = '/etc/smartbridge.ini'
SmartbridgeConfigLocations = [SmartbridgeConfigPath]
UserConfigPath = os.path.join(expanduser('~'), '.smartbridge')
SmartbridgeConfigLocations.append(UserConfigPath)


class BaseConfiguration(Configuration):

    def __init__(self, user_config):
        self.update(user_config)

    @property
    def debug_mode(self):
        """
        A flag indicating whether Smartbridge is in debug mode. Setting
        this to True will cause the underlying provider's debug
        output to be turned on.
        The flag can be toggled by sending in the smartbridge_debug value via
        the config dictionary, or setting the SB_DEBUG environment variable.
        :rtype: ``bool``
        :return: Whether debug mode is on.
        """
        return self.get('smartbridge_debug', os.environ.get('SB_DEBUG', False))


class BaseProvider(Provider):

    def __init__(self, config):
        self._config = BaseConfiguration(config)
        self._config_parser = ConfigParser()
        self._config_parser.read(SmartbridgeConfigLocations)

    @property
    def config(self):
        return self._config

    @property
    def name(self):
        return str(self.__class__.__name__)

    def authenticate(self):
        """
        A basic implementation which simply runs a low impact command to
        check whether credentials work. Providers should override with
        more efficient implementations.
        """
        log.debug("Checking if credential works...")
        try:
            self.refresh()
            return True
        except Exception as e:
            log.exception("ProviderConnectionException occurred")
            raise ProviderConnectionException(
                "Authentication with provider failed: %s" % (e,))

    def clone(self, zone=None):
        cloned_config = self.config.copy()
        cloned_provider = self.__class__(cloned_config)
        return cloned_provider

    def has_service(self, device_type):
        """
        Checks whether this provider supports a given service.
        :type device_type: str or :class:``.DeviceType``
        :param device_type: Type of device to check support for.
        :rtype: bool
        :return: ``True`` if the device type is supported.
        """
        log.info("Checking if provider supports %s", device_type)
        try:
            if self._deepgetattr(self, device_type):
                log.info("This provider supports %s", device_type)
                return True
        except AttributeError:
            pass  # Undefined device_type type
        except NotImplementedError:
            pass  # device_type not implemented
        log.info("This provider doesn't support %s", device_type)
        return False

    def _deepgetattr(self, obj, attr):
        """Recurses through an attribute chain to get the ultimate value."""
        return functools.reduce(getattr, attr.split('.'), obj)

    def _get_config_value(self, key, default_value=None):
        """
        A convenience method to extract a configuration value.
        :type key: str
        :param key: a field to look for in the ``self.config`` field
        :type default_value: anything
        :param default_value: the default value to return if a value for the
                              ``key`` is not available
        :return: a configuration value for the supplied ``key``
        """
        log.debug("Getting config key %s, with supplied default value: %s",
                  key, default_value)
        value = default_value
        if isinstance(self.config, dict) and self.config.get(key):
            value = self.config.get(key, default_value)
        elif hasattr(self.config, key) and getattr(self.config, key):
            value = getattr(self.config, key)
        elif (self._config_parser.has_option(self.PROVIDER_ID, key) and
              self._config_parser.get(self.PROVIDER_ID, key)):
            value = self._config_parser.get(self.PROVIDER_ID, key)
        return value
