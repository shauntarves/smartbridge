"""
Base implementation for services available through a provider
"""
import logging

from smartbridge.interfaces.services import ProviderService
from smartbridge.interfaces.services import SessionService
from smartbridge.interfaces.services import DeviceService
from smartbridge.interfaces.services import SwitchableDeviceService
from smartbridge.interfaces.services import BulbService
from smartbridge.interfaces.services import VacuumService
from smartbridge.interfaces.services import PlugService
from smartbridge.interfaces.services import SensorService
from smartbridge.interfaces.services import ContactSensorService
from smartbridge.interfaces.services import MotionSensorService

log = logging.getLogger(__name__)


class BaseProviderService(ProviderService):

    def __init__(self, provider):
        self._service_event_pattern = "provider"
        self._provider = provider

    @property
    def provider(self):
        return self._provider


class BaseSessionService(BaseProviderService, SessionService):

    def __init__(self, provider):
        super(BaseSessionService, self).__init__(provider)


class BaseDeviceService(BaseProviderService, DeviceService):

    def __init__(self, provider):
        super(BaseDeviceService, self).__init__(provider)


class BaseSwitchableDeviceService(BaseDeviceService, SwitchableDeviceService):

    def __init__(self, provider):
        super(BaseSwitchableDeviceService, self).__init__(provider)


class BaseBulbService(BaseSwitchableDeviceService, BulbService):

    def __init__(self, provider):
        super(BaseBulbService, self).__init__(provider)
        self._service_event_pattern += ".bulbs"


class BasePlugService(BaseSwitchableDeviceService, PlugService):

    def __init__(self, provider):
        super(BasePlugService, self).__init__(provider)
        self._service_event_pattern += ".plugs"


class BaseVacuumService(BaseDeviceService, VacuumService):

    def __init__(self, provider):
        super(BaseVacuumService, self).__init__(provider)
        self._service_event_pattern += ".vacuums"


class BaseSensorService(BaseDeviceService, SensorService):

    def __init__(self, provider):
        super(BaseSensorService, self).__init__(provider)
        self._service_event_pattern += ".sensors"


class BaseContactSensorService(BaseSensorService, ContactSensorService):

    def __init__(self, provider):
        super(BaseContactSensorService, self).__init__(provider)
        self._service_event_pattern += ".contact"


class BaseMotionSensorService(BaseSensorService, MotionSensorService):

    def __init__(self, provider):
        super(BaseMotionSensorService, self).__init__(provider)
        self._service_event_pattern += ".motion"
