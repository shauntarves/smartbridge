"""
Specifications for services available through a provider
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty


class ProviderService(object):
    """
    Base interface for any service supported by a provider. This interface
    has a provider property that can be used to access the provider associated
    with this service.
    """
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def provider(self):
        """
        Returns the provider instance associated with this service.
        :rtype: :class:`.Provider`
        :return: a Provider object
        """
        pass


class SessionService(ProviderService):

    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, config):
        pass

    @abstractmethod
    def refresh(self, session):
        pass

    @abstractmethod
    def destroy(self, session):
        pass


class DeviceService(ProviderService):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, device_id):
        """
        Returns a Device given its ID or ``None`` if not found.

        :type device_id: ``str``
        :param device_id: The ID of the device to retrieve.
        :rtype: ``object`` of :class:`.Device`
        :return: a Device object
        """
        pass

    @abstractmethod
    def list(self):
        """
        List all devices.

        :rtype: ``list`` of :class:`.Device`
        :return: list of Device objects
        """
        pass


class SwitchableDeviceService(DeviceService):
    """
    The switchable device service interface is a collection of services
    that provides access to the underlying smart device services that
    can be switched on and off in a provider.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def switch_on(self, plug):
        """
        Switch on a Device.

        :type device: ``str`` or :class:`.Device`
        :param device: The object or id of the device to be switched on.
        """
        pass

    @abstractmethod
    def switch_off(self, device):
        """
        Switch off a Device.

        :type device: ``str`` or :class:`.Device`
        :param device: The object or id of the device to be switched off.
        """
        pass


class PlugService(SwitchableDeviceService):
    """
    The plug service interface is a collection of services that provides
    access to the underlying smart plug services in a provider.
    """
    __metaclass__ = ABCMeta


class BulbService(SwitchableDeviceService):
    """
    The bulb service interface is a collection of services that provides
    access to the underlying smart bulb services in a provider.
    """
    __metaclass__ = ABCMeta


class VacuumService(DeviceService):
    """
    The vacuum service interface is a collection of services that provides
    access to the underlying smart vacuum services in a provider.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self, vacuum):
        """
        Start a Vacuum.

        :type vacuum: ``str`` or :class:`.Vacuum`
        :param vacuum: The object or id of the vacuum to be started.
        """
        pass

    @abstractmethod
    def dock(self, vacuum):
        """
        Dock a Vacuum.

        :type vacuum: ``str`` or :class:`.Vacuum`
        :param vacuum: The object or id of the vacuum to be docked.
        """
        pass

    @abstractmethod
    def pause(self, vacuum):
        """
        Pause a Vacuum.

        :type vacuum: ``str`` or :class:`.Vacuum`
        :param vacuum: The object or id of the vacuum to be paused.
        """
        pass


class SensorService(DeviceService):
    """
    The sensor service interface is a collection of services that provides
    access to the underlying smart sensor services in a provider.
    """
    __metaclass__ = ABCMeta
