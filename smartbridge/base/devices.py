"""
Base implementation for data objects exposed through a provider or service
"""

from abc import abstractmethod
import inspect
import logging
import re

from smartbridge.interfaces.devices import Configuration
from smartbridge.interfaces.devices import Device
from smartbridge.interfaces.devices import NetworkedDevice
from smartbridge.interfaces.devices import Sensor
from smartbridge.interfaces.devices import ContactSensor
from smartbridge.interfaces.devices import MotionSensor
from smartbridge.interfaces.devices import Bulb
from smartbridge.interfaces.devices import Plug
from smartbridge.interfaces.devices import SwitchableDevice
from smartbridge.interfaces.devices import Vacuum

log = logging.getLogger(__name__)


class BaseDevice(Device):
    """
    Base implementation of a smartbridge Device.
    """

    def __init__(self, provider, device):
        self.__provider = provider
        self._device = device

    @property
    def _provider(self):
        return self.__provider

    def to_json(self):
        # Get all attributes but filter methods and private/magic ones
        attr = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
        js = {k: v for(k, v) in attr if not k.startswith('_')}
        return js

    def __repr__(self):
        name_or_label = getattr(self, 'label', self.name)
        if name_or_label == self.id:
            return "<Smartbridge-{0}: {1}>".format(
                self.__class__.__name__, self.id)
        else:
            return "<Smartbridge-{0}: {1} ({2})>".format(
                self.__class__.__name__, name_or_label, self.id)

    def __eq__(self, other):
        return (isinstance(other, Device) and
                # pylint:disable=protected-access
                self._provider == other._provider and
                self.id == other.id)


class BaseNetworkedDevice(BaseDevice, NetworkedDevice):

    def __init__(self, provider, device):
        super(BaseNetworkedDevice, self).__init__(provider, device)


class BaseSwitchableDevice(BaseNetworkedDevice, SwitchableDevice):

    def __init__(self, provider, device):
        super(BaseSwitchableDevice, self).__init__(provider, device)


class BaseBulb(BaseSwitchableDevice, Bulb):

    def __init__(self, provider, bulb):
        super(BaseBulb, self).__init__(provider, bulb)

    def __eq__(self, other):
        return (isinstance(other, BaseBulb) and
                # pylint:disable=protected-access
                self._provider == other._provider and
                self.id == other.id)

    def switch_on(self):
        return self._provider.bulb.switch_on(self)

    def switch_off(self):
        return self._provider.bulb.switch_off(self)


class BasePlug(BaseSwitchableDevice, Plug):

    def __init__(self, provider, plug):
        super(BasePlug, self).__init__(provider, plug)

    def switch_on(self):
        return self._provider.plug.switch_on(self)

    def switch_off(self):
        return self._provider.plug.switch_off(self)


class BaseSensor(BaseDevice):

    def __init__(self, provider, sensor):
        super(BaseSensor, self).__init__(provider, sensor)


class BaseContactSensor(BaseSensor, ContactSensor):

    def __init__(self, provider, sensor):
        super(BaseContactSensor, self).__init__(provider, sensor)


class BaseMotionSensor(BaseSensor, MotionSensor):

    def __init__(self, provider, sensor):
        super(BaseMotionSensor, self).__init__(provider, sensor)


class BaseVacuum(BaseNetworkedDevice, Vacuum):

    def __init__(self, provider, vacuum):
        super(BaseVacuum, self).__init__(provider, vacuum)

    def clean(self):
        return self._provider.vacuum.clean(self)

    def pause(self):
        return self._provider.vacuum.pause(self)

    def dock(self):
        return self._provider.vacuum.dock(self)
