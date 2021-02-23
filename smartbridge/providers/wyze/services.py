import logging
from smartbridge.interfaces.devices import VacuumSuction

from smartbridge.base.services import BaseSessionService
from smartbridge.base.services import BaseBulbService
from smartbridge.base.services import BasePlugService
from smartbridge.base.services import BaseVacuumService
from smartbridge.interfaces.exceptions import ProviderConnectionException, InvalidValueException

from .devices import WyzeBulb
from .devices import WyzePlug
from .devices import WyzeVacuum

log = logging.getLogger(__name__)


class WyzeSessionService(BaseSessionService):

    def __init__(self, provider):
        super(WyzeSessionService, self).__init__(provider)

    def create(self, config):
        try:
            session = self.provider.wyze_client.login(
                config['username'], config['password'])
            return session
        except ProviderConnectionException:
            return None


class WyzeBulbService(BaseBulbService):

    def __init__(self, provider):
        super(WyzeBulbService, self).__init__(provider)

    def list(self):
        wyze_bulbs = self.provider.wyze_client.list_bulbs()
        return [WyzeBulb(self.provider, bulb) for bulb in wyze_bulbs]

    def get(self, bulb_mac):
        try:
            bulb = self.provider.wyze_client.get_bulb(
                bulb_mac, WyzeBulb.pids())
            return WyzeBulb(self.provider, bulb)
        except ProviderConnectionException:
            return None

    def set_color_temp(self, bulb, value: int):
        pid = WyzeBulb.color_temp_pid()
        if pid is not None:
            try:
                self.provider.wyze_client.set_bulb_property(
                    bulb.mac, bulb.model, pid, value)
            except ProviderConnectionException as e:
                raise e
        else:
            raise InvalidValueException(
                "color_temp_pid() must return a value.")

    def set_brightness(self, bulb, value:int):
        pid = WyzeBulb.brightness_pid()
        if pid is not None:
            try:
                self.provider.wyze_client.set_bulb_property(
                    bulb.mac, bulb.model, pid, value)
            except ProviderConnectionException as e:
                raise e
        else:
            raise InvalidValueException(
                "brightness_pid() must return a value.")

    def switch_on(self, bulb):
        props = WyzeBulb.switch_on_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_bulb_property(
                    bulb.mac, bulb.model, prop[0], prop[1])
            except ProviderConnectionException as e:
                raise e
        else:
            raise InvalidValueException(
                "switch_on_props() must return at least one property.")

    def switch_off(self, bulb):
        props = WyzeBulb.switch_off_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_bulb_property(
                    bulb.mac, bulb.model, prop[0], prop[1])
            except ProviderConnectionException as e:
                raise e
        else:
            raise InvalidValueException(
                "switch_off_props() must return at least one property.")


class WyzePlugService(BasePlugService):

    def __init__(self, provider):
        super(WyzePlugService, self).__init__(provider)

    def list(self):
        wyze_plugs = self.provider.wyze_client.list_plugs()
        return [WyzePlug(self.provider, plug) for plug in wyze_plugs]

    def get(self, plug_mac):
        try:
            plug = self.provider.wyze_client.get_plug(
                plug_mac, WyzePlug.pids())
            return WyzePlug(self.provider, plug)
        except ProviderConnectionException:
            return None

    def switch_on(self, plug):
        props = WyzePlug.switch_on_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_plug_property(
                    plug.mac, plug.model, prop[0], prop[1])
            except ProviderConnectionException:
                return None
        else:
            raise InvalidValueException(
                "switch_on_props() must return at least one property.")

    def switch_off(self, plug):
        props = WyzePlug.switch_off_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_plug_property(
                    plug.mac, plug.model, prop[0], prop[1])
            except ProviderConnectionException:
                return None
        else:
            raise InvalidValueException(
                "switch_off_props() must return at least one property.")


class WyzeVacuumService(BaseVacuumService):

    def __init__(self, provider):
        super(WyzeVacuumService, self).__init__(provider)

    def list(self):
        wyze_vacuums = self.provider.wyze_client.list_vacuums()
        return [WyzeVacuum(self.provider, vac) for vac in wyze_vacuums]

    def get(self, vacuum_mac):
        try:
            vacuum = self.provider.wyze_client.get_vacuum(
                vacuum_mac, WyzeVacuum.pids(), WyzeVacuum.device_info_pids())
            return WyzeVacuum(self.provider, vacuum)
        except ProviderConnectionException:
            return None

    def clean(self, vacuum):
        props = WyzeVacuum.clean_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_vacuum_mode(
                    vacuum.mac, vacuum.model, prop[0], prop[1])
                self.provider.wyze_client.create_user_vacuum_event(
                    'WRV_CLEAN', 1)
            except ProviderConnectionException:
                return None
        else:
            raise InvalidValueException(
                "clean_props() must return at least one property.")

    def pause(self, vacuum):
        props = WyzeVacuum.pause_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_vacuum_mode(
                    vacuum.mac, vacuum.model, prop[0], prop[1])
                self.provider.wyze_client.create_user_vacuum_event(
                    'WRV_PAUSE', 1)
            except ProviderConnectionException:
                return None
        else:
            raise InvalidValueException(
                "pause_props() must return at least one property.")

    def dock(self, vacuum):
        props = WyzeVacuum.dock_props()
        if len(props) == 1:
            prop = props.popitem()
            try:
                self.provider.wyze_client.set_vacuum_mode(
                    vacuum.mac, vacuum.model, prop[0], prop[1])
                # yes, when canceling cleaning, the event is still WRV_CLEAN
                self.provider.wyze_client.create_user_vacuum_event(
                    'WRV_CLEAN', 1)
            except ProviderConnectionException:
                return None
        else:
            raise InvalidValueException(
                "dock_props() must return at least one property.")

    def set_suction_level(self, vacuum_mac, vacuum_model, value):
        try:
            suction_level_code = (
                value.code if isinstance(
                    value, VacuumSuction) else value)
            props = WyzeVacuum.suction_level_props()
            self.provider.wyze_client.set_vacuum_preference(
                vacuum_mac, vacuum_model, props['control_type'], suction_level_code)
            self.provider.wyze_client.create_user_vacuum_event(
                props['event_id'], 1)
        except ProviderConnectionException:
            return None
