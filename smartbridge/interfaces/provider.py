"""
Specification for a provider interface
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty


class Provider(object):
    """
    Base interface for a provider
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config):
        """
        Create a new provider instance given a dictionary of
        configuration attributes.
        :type config: :class:`dict`
        :param config: A dictionary object containing provider initialization
                       values. Alternatively, this can be an iterable of
                       key/value pairs (as tuples or other iterables of length
                       two). See specific provider implementation for the
                       required fields.
        :rtype: :class:`.Provider`
        :return:  a concrete provider instance
        """
        pass

    @abstractproperty
    def config(self):
        """
        Returns the config object associated with this provider. This object
        is a subclass of :class:`dict` and will contain the properties
        provided at initialization time, grouped under `provide_properties` and
        `credentials` keys. In addition, it also contains extra provider-wide
        properties such as the default result limit for `list()` queries.
        Example:
        .. code-block:: python
            config = { 'access_token' : '<my_key>' }
            provider = factory.create_provider(ProviderList.WYZE, config)
            print(provider.config['credentials'].get('wyze_access_token'))
            print(provider.config.default_result_limit))
            # change provider result limit
            provider.config.default_result_limit = 100
        :rtype: :class:`.Configuration`
        :return:  An object of class Configuration, which contains the values
                  used to initialize the provider, as well as other global
                  configuration properties.
        """
        pass

    @abstractmethod
    def authenticate(self):
        """
        Checks whether a provider can be successfully authenticated with the
        configured settings. Clients are *not* required to call this method
        prior to accessing provider services, as most connections are
        initialized lazily. The authenticate() method will return True if
        smartbridge can establish a successful connection to the provider.
        It will raise an exception with the appropriate error details
        otherwise.
        Example:
        .. code-block:: python
            try:
                if provider.authenticate():
                   print("Provider connection successful")
            except ProviderConnectionException as e:
                print("Could not authenticate with provider: %s" % (e, ))
        :rtype: :class:`bool`
        :return: ``True`` if authentication is successful.
        """
        pass

    @abstractmethod
    def has_service(self, service_type):
        """
        Checks whether this provider supports a given service.
        Example:
        .. code-block:: python
            if provider.has_service(DeviceType.PLUG):
               print("Provider supports plug services")
               provider.plug.list()
        :type service_type: :class:`.DeviceType`
        :param service_type: Type of device to check support for.
        :rtype: :class:`bool`
        :return: ``True`` if the device type is supported.
        """
        pass

    @abstractproperty
    def plug(self):
        """
        Provides access to all plug-related services in this provider.
        Example:
        .. code-block:: python
            plugs = provider.plug.list()
            plug = provider.plug.get('abcd1234')
        :rtype: :class:`.PlugService`
        :return:  a PlugService object
        """
        pass

    @abstractproperty
    def vacuum(self):
        """
        Provides access to all vacuum-related services in this provider.
        Example:
        .. code-block:: python
            vacuums = provider.vacuum.list()
            vacuum = provider.vacuum.get('abcd1234')
        :rtype: :class:`.VacuumService`
        :return:  a VacuumService object
        """
        pass

    @abstractproperty
    def bulb(self):
        """
        Provides access to all bulb-related services in this provider.
        Example:
        .. code-block:: python
            bulbs = provider.bulb.list()
        :rtype: :class:`.BulbService`
        :return:  a BulbService object
        """
        pass

    @abstractproperty
    def contact_sensor(self):
        """
        Provides access to all contact sensor-related services in this provider.
        Example:
        .. code-block:: python
            bulbs = provider.contact_sensor.list()
        :rtype: :class:`.ContactSensorService`
        :return:  a ContactSensorService object
        """
        pass

    @abstractproperty
    def motion_sensor(self):
        """
        Provides access to all motion sensor-related services in this provider.
        Example:
        .. code-block:: python
            bulbs = provider.motion_sensor.list()
        :rtype: :class:`.MotionSensorService`
        :return:  a MotionSensorService object
        """
        pass
