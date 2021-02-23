"""
Specifications for data objects exposed through a ``provider`` or ``service``.
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from enum import Enum


class Configuration(dict):
    """
    Represents a Smartbridge configuration object
    """

    @abstractproperty
    def debug_mode(self):
        """
        A flag indicating whether Smartbridge is in debug mode.
        Setting this to ``True`` will cause the underlying provider's debug
        output to be turned on. The flag can be toggled by sending in the
        ``smartbridge_debug`` value via the config dictionary, or setting the
        ``SMARTBRIDGE_DEBUG`` environment variable.
        :rtype: ``bool``
        :return: Whether debug mode is on.
        """


class DeviceType(object):
    """
    Defines possible service types that are offered by providers.
    Providers can implement the ``has_service`` method and clients can check
    for the availability of a service with::
        if (provider.has_service(DeviceType.BULB))
            ...
    """

    LIGHT = 'light'
    LOCK = 'lock'
    PLUG = 'plug'
    CONTACT_SENSOR = 'sensor.contact'
    MOTION_SENSOR = 'sensor.motion'
    VACUUM = 'vacuum'


class Device(object):
    """
    Base interface for any Device supported by a provider.

    This interface has a  _provider property that can be used to access the
    provider associated with the resource, which is only intended for use by
    subclasses. Every Smartbridge resource also has an id, a model, and a
    name property. The id property is a unique identifier for the resource.
    The name is a more user-friendly version of an id, suitable for
    display to an end-user. However, it cannot be used in place of id. See
    @name documentation.
    """
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def _provider(self):
        """
        Returns the provider instance associated with this device.
        Intended for use by subclasses only.
        :rtype: :class:`.Provider`
        :return: a Provider object
        """
        pass

    @property
    @abstractmethod
    def id(self):
        """
        Get the device identifier.

        The id property is used to uniquely identify the resource, and is an
        opaque value which should not be interpreted by Smartbridge clients,
        and is a value meaningful to the underlying provider.
        :rtype: ``str``
        :return: ID for this resource as returned by the provider.
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """
        Get the name id for the device.

        The name property is typically a user-friendly id value for the
        resource. The name is different from the id property in the following
        ways:
         1. The name property is often a more user-friendly value to
            display to the user than the id property.
         2. The name may sometimes be the same as the id, but should never
            be used in place of the id.
         3. The id is what will uniquely identify a resource, and will be used
            internally by Smartbridge for all get operations etc.
         4. All resources have a name.
         5. The name is read-only.
         6. However, the name may not necessarily be unique, which is the
            reason why it should not be used for uniquely identifying a
            resource.
        :rtype: ``str``
        :return: name for this resource as returned by the provider.
        """
        pass

    @property
    @abstractmethod
    def mac(self):
        """
        Get the MAC address of the device.

        :rtype: ``str``
        :return: MAC address for this device as returned by the provider.
        """
        pass

    @property
    @abstractmethod
    def model(self):
        """
        Get the product model of the device.

        :rtype: ``str``
        :return: product model for this resource as returned by the provider.
        """
        pass

    @abstractmethod
    def to_json(self):
        """
        Returns a JSON representation of the Device object.
        """
        pass


class NetworkedDevice(Device):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def ip(self):
        """
        Get the device IP address.

        Some devices may not support being networked, in which case, a
        ``NotImplementedError`` will be thrown.
        :rtype: ``str``
        :return: IP address for this device as returned by the provider.
        :raise: ``NotImplementedError`` if this device does not support
                networking.
        """
        pass

    @property
    @abstractmethod
    def rssi(self):
        """
        Get the device RSSI.

        Some devices may not support being networked, in which case, a
        ``NotImplementedError`` will be thrown.
        :rtype: ``str``
        :return: RSSI for this device as returned by the provider.
        :raise: ``NotImplementedError`` if this device does not support
                networking.
        """
        pass

    @property
    @abstractmethod
    def ssid(self):
        """
        Get the device SSID.

        Some device may not support being wirelessly networked, in which case, a
        ``NotImplementedError`` will be thrown.
        :rtype: ``str``
        :return: SSID for this device as returned by the provider.
        :raise: ``NotImplementedError`` if this device does not support
                wireless networking.
        """
        pass


class SwitchState(Enum):
    """
    Standard states for a switch.
    """
    ON = 'on'
    OFF = 'off'


class SwitchableDevice(NetworkedDevice):

    __metaclass__ = ABCMeta

    @abstractmethod
    def switch_on(self):
        """
        Turn on this switch.
        """
        pass

    @abstractmethod
    def switch_off(self):
        """
        Turn off this switch.
        """
        pass

    @property
    @abstractmethod
    def switch_state(self):
        """
        Get the state of the switch.

        :rtype: :class:`.SwitchState`
        :return: a SwitchState object
        """
        pass


class Bulb(SwitchableDevice):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def brightness(self):
        """
        Get the bulb brightness.

        :rtype: ``int``
        :return: current brightness for this bulb as returned by the provider.
        """
        pass

    @property
    @abstractmethod
    def color_temp(self):
        """
        Get the bulb color temperature.

        :rtype: ``int``
        :return: current color temperature for this bulb as returned by the provider.
        """
        pass


class VacuumMode(Enum):
    BREAK_POINT = 'break point'
    IDLE = 'idle'
    PAUSE = 'pause'
    SWEEPING = 'sweeping'
    ON_WAY_CHARGE = 'on way charge'
    FULL_FINISH_SWEEPING_ON_WAY_CHARGE = 'full finish sweeping on way charge'


class VacuumSuction(Enum):
    QUIET = (1, 'Quiet')
    STANDARD = (2, 'Standard')
    STRONG = (3, 'Strong')

    def __init__(self, code, label):
        self._code = code
        self._label = label

    @property
    def code(self):
        return self._code

    @property
    def label(self):
        return self._label


class Vacuum(NetworkedDevice):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def current_position(self):
        """
        Get the current Vacuum position.

        :rtype: :class:`dict`
        :return: a dict object
        """
        pass

    @property
    @abstractmethod
    def current_map(self):
        """
        Get the latest Vacuum map.

        :rtype: :class:`dict`
        :return: a dict object
        """
        pass

    @property
    @abstractmethod
    def suction_level(self):
        """
        Get the Vacuum suction level.

        :rtype: :class:`.VacuumSuction`
        :return: a VacuumSuction object
        """
        pass

    @property
    @abstractmethod
    def mode(self):
        """
        Get the Vacuum cleaning mode.

        :rtype: :class:`.VacuumMode`
        :return: a VacuumMode object
        """
        pass

    @property
    @abstractmethod
    def battery(self):
        """
        Get the device battery level.

        :rtype: ``int``
        :return: current battery level for this device as returned by the provider.
        """
        pass

    @abstractmethod
    def clean(self):
        """
        Start the Vacuum.
        """
        pass

    @abstractmethod
    def pause(self):
        """
        Pause the Vacuum.
        """
        pass

    @abstractmethod
    def dock(self):
        """
        Dock the Vacuum.
        """
        pass


class Plug(SwitchableDevice):

    __metaclass__ = ABCMeta


class Sensor(Device):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def rssi(self):
        """
        Get the device RSSI.

        Some devices may not reort RSSI, in which case, a
        ``NotImplementedError`` will be thrown.
        :rtype: ``str``
        :return: RSSI for this device as returned by the provider.
        :raise: ``NotImplementedError`` if this device does not report RSSI.
        """
        pass

    @property
    @abstractmethod
    def voltage(self):
        """
        Get the device voltage.

        Some devices may not report voltage, in which case, a
        ``NotImplementedError`` will be thrown.
        :rtype: ``str``
        :return: Voltage for this device as returned by the provider.
        :raise: ``NotImplementedError`` if this device does not report voltage.
        """
        pass


class MotionSensor(Sensor):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def motion_state(self):
        pass

    @property
    @abstractmethod
    def motion_state_ts(self):
        pass


class ContactSensor(Sensor):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def open_close_state(self):
        pass

    @property
    @abstractmethod
    def open_close_state_ts(self):
        pass
