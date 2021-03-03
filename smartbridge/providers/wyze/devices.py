"""
DataTypes used by this provider
"""

from abc import abstractmethod
import base64
import logging

from smartbridge.interfaces.devices import VacuumMode
from smartbridge.interfaces.devices import VacuumSuction
from smartbridge.interfaces.exceptions import InvalidParamException, InvalidValueException
from smartbridge.base.devices import BaseDevice
from smartbridge.base.devices import BaseNetworkedDevice
from smartbridge.base.devices import BaseSwitchableDevice
from smartbridge.base.devices import BaseBulb
from smartbridge.base.devices import BasePlug
from smartbridge.base.devices import BaseVacuum
from smartbridge.base.devices import BaseSensor
from smartbridge.base.devices import BaseMotionSensor
from smartbridge.base.devices import BaseContactSensor
from enum import Enum

log = logging.getLogger(__name__)


class DeviceModels(object):
    """
    Defines the model-to-device type mapping for the Wyze service provider.
    """
    BULB = ['WLPA19', 'WLPA19C']
    LOCK = ['YD.LO1']
    PLUG = ['WLPP1', 'WLPP1CFH']
    CONTACT_SENSOR = ['DWS3U']
    MOTION_SENSOR = ['PIR3U']
    VACUUM = ['JA_RO2']


class WyzeDevice(BaseDevice):

    def __init__(self, provider, device):
        super(WyzeDevice, self).__init__(provider, device)

    @property
    def id(self):
        return self.mac

    @property
    def mac(self):
        return self._device['mac']

    @property
    def model(self):
        return self._device['product_model']

    @property
    def name(self):
        return self._device['nickname']

    @abstractmethod
    def _set_property(self, name, value):
        pass

    @abstractmethod
    def _get_property(self, name, default=None):
        pass


class WyzeNetworkedDevice(WyzeDevice, BaseNetworkedDevice):

    def __init__(self, provider, device):
        super(WyzeNetworkedDevice, self).__init__(provider, device)

    @property
    def ip(self):
        return self._get_property('ip')

    @property
    def rssi(self):
        return self._get_property('rssi')

    @property
    def ssid(self):
        return self._get_property('ssid')


class WyzeSwitchableDevice(WyzeNetworkedDevice, BaseSwitchableDevice):

    def __init__(self, provider, device):
        super(WyzeSwitchableDevice, self).__init__(provider, device)

    @property
    def switch_state(self):
        return self._get_property('switch_state')

    @property
    @abstractmethod
    def switch_on_props(self):
        pass

    @property
    @abstractmethod
    def switch_off_props(self):
        pass


class WyzeBulb(WyzeSwitchableDevice, BaseBulb):

    def __init__(self, provider, bulb):
        super(WyzeBulb, self).__init__(provider, bulb)

    @property
    def color_temp(self):
        return self._get_property('color_temp')

    @color_temp.setter
    def color_temp(self, value: int):
        if value is None or not isinstance(value, int):
            raise InvalidParamException('color_temp', value)

        if value < 2700 or value > 6500:
            raise InvalidValueException('color_temp', value)

        self._set_property('color_temp', value)
        self._provider.bulb.set_color_temp(self, value)

    @property
    def away_mode(self):
        return self._get_property('away_mode')

    @away_mode.setter
    def away_mode(self, value: str):
        if value is None or not isinstance(value, str):
            raise InvalidParamException('away_mode', value)
        
        # setting away mode to true requires complicated rules and actions
        # so we only allow turning it off for now
        if value != 0: 
            raise InvalidValueException('away_mode', value)

        self._set_property('away_mode', value)
        self._provider.bulb.set_away_mode(self.mac, self.model, value)

    @property
    def power_loss_recovery(self):
        return self._get_property('power_loss_recovery')

    @power_loss_recovery.setter
    def power_loss_recovery(self, value: int):
        if value is None or not isinstance(value, int):
            raise InvalidParamException('power_loss_recovery', value)

        if value != 0 or value != 1:
            raise InvalidValueException('power_loss_recovery', value)

        self._set_property('power_loss_recovery', value)
        self._provider.bulb.set_power_loss_recovery(self.mac, self.model, value)

    @property
    def brightness(self):
        return self._get_property('brightness')

    @brightness.setter
    def brightness(self, value: int):
        if value is None or not isinstance(value, int):
            raise InvalidParamException('brightness', value)

        if value < 0 or value > 100:
            raise InvalidValueException('brightness', value)

        self._set_property('brightness', value)
        self._provider.bulb.set_brightness(self, value)

    def switch_on_props():
        return { WyzeBulb.props().get('switch_state')[0]: "1" }

    def switch_off_props():
        return { WyzeBulb.props().get('switch_state')[0]: "0" }

    def brightness_pid():
        return WyzeBulb.props().get('brightness')[0]

    def color_temp_pid():
        return WyzeBulb.props().get('color_temp')[0]

    @staticmethod
    def props():
        return {
            "switch_state": ("P3", "int"),
            "available": ("P5", "int"),
            "brightness": ("P1501", "int"),
            "color_temp": ("P1502", "int"),
            # "": ("P1503", ""), not used?
            # "": ("P1505", ""), not used?
            "away_mode": ("P1506", "str"),
            "power_loss_recovery": ("P1509", "int"),
        }

    @staticmethod
    def pids():
        return [prop[0] for prop in WyzeBulb.props().values()]

    def _set_property(self, name, value):
        if name in self._device:
            self._device[name] = value
        elif 'data' in self._device and 'property_list' in self._device['data']:
            if name in self._device['data']['property_list']:
                self._device['data']['property_list'][name] = value
            else:
                prop_def = WyzeBulb.props().get(name)
                if prop_def[0] in self._device['data']['property_list']:
                    self._device['data']['property_list'][prop_def[0]] = value
        elif 'device_params' in self._device and name in self._device['device_params']:
            if name in self._device['device_params']:
                self._device['device_params'][name] = value
            else:
                prop_def = WyzeBulb.props().get(name)
                if prop_def[0] in self._device['device_params']:
                    self._device['device_params'][prop_def[0]] = value

    def _get_property(self, name, default=None):
        if name in self._device:
            return self._device[name]
        elif 'data' in self._device and 'property_list' in self._device['data']:
            for property in self._device['data']['property_list']:
                prop_def = WyzeBulb.props().get(name)
                if (prop_def[0] == property['pid']):
                    return property['value']
        elif 'device_params' in self._device and name in self._device['device_params']:
            return self._device['device_params'][name]

        return default


class WyzePlug(WyzeSwitchableDevice, BasePlug):

    def __init__(self, provider, plug):
        super(WyzePlug, self).__init__(provider, plug)

    def switch_on_props():
        return { WyzePlug.props().get('switch_state')[0]: "1" }

    def switch_off_props():
        return { WyzePlug.props().get('switch_state')[0]: "0" }

    @staticmethod
    def props():
        return {
            "switch_state": ("P3", "int"),
            "available": ("P5", "int"),
            "status_light": ("P13", "int"),
            "rssi": ("P1612", "str"),
            "away_mode": ("P1614", "str"),
        }

    @staticmethod
    def pids():
        return [prop[0] for prop in WyzePlug.props().values()]

    def _set_property(self, name, value):
        if name in self._device:
            self._device[name] = value
        elif 'data' in self._device and 'property_list' in self._device['data'] and name in self._device['data']['property_list']:
            self._device['data']['property_list'][name] = value
        elif 'device_params' in self._device and name in self._device['device_params']:
            self._device['device_params'][name] = value

    def _get_property(self, name, default=None):
        if name in self._device:
            return self._device[name]
        elif 'data' in self._device and 'property_list' in self._device['data']:
            for property in self._device['data']['property_list']:
                prop_def = WyzePlug.props().get(name)
                if (prop_def[0] == property['pid']):
                    return property['value']
        elif 'device_params' in self._device and name in self._device['device_params']:
            return self._device['device_params'][name]

        return default


class WyzeVacuumMapRoom(object):

    def __init__(self, *, id = None, name = None, clean_state = None, room_clean = None, **others: dict):
        self.id = id
        self.name = name
        self.clean_state = clean_state
        self.room_clean = room_clean


class WyzeVacuum(WyzeDevice, BaseVacuum):

    _modes = {
        11: VacuumMode.BREAK_POINT,
        33: VacuumMode.BREAK_POINT,
        39: VacuumMode.BREAK_POINT,
        10: VacuumMode.FULL_FINISH_SWEEPING_ON_WAY_CHARGE,
        12: VacuumMode.FULL_FINISH_SWEEPING_ON_WAY_CHARGE,
        26: VacuumMode.FULL_FINISH_SWEEPING_ON_WAY_CHARGE,
        32: VacuumMode.FULL_FINISH_SWEEPING_ON_WAY_CHARGE,
        38: VacuumMode.FULL_FINISH_SWEEPING_ON_WAY_CHARGE,
        0: VacuumMode.IDLE,
        14: VacuumMode.IDLE,
        29: VacuumMode.IDLE,
        35: VacuumMode.IDLE,
        40: VacuumMode.IDLE,
        5: VacuumMode.ON_WAY_CHARGE,
        4: VacuumMode.PAUSE,
        9: VacuumMode.PAUSE,
        27: VacuumMode.PAUSE,
        31: VacuumMode.PAUSE,
        37: VacuumMode.PAUSE,
        1: VacuumMode.SWEEPING,
        7: VacuumMode.SWEEPING,
        25: VacuumMode.SWEEPING,
        30: VacuumMode.SWEEPING,
        36: VacuumMode.SWEEPING,
    }

    _suction_levels = {
        1: VacuumSuction.QUIET,
        2: VacuumSuction.STANDARD,
        3: VacuumSuction.STRONG,
    }

    """
    The protobuf definition for a vacuum map
    """
    _robot_map_proto = {
      '1': {'type': 'int', 'name': 'mapType_'},
      '2': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'taskBeginDate_'},
        '2': {'type': 'int', 'name': 'mapUploadDate_'}
        }, 'name': 'mapExtInfo_'},
      '3': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'mapHeadId_'},
        '2': {'type': 'int', 'name': 'sizeX_'},
        '3': {'type': 'int', 'name': 'sizeY_'},
        '4': {'type': 'float', 'name': 'minX_'},
        '5': {'type': 'float', 'name': 'minY_'},
        '6': {'type': 'float', 'name': 'maxX_'},
        '7': {'type': 'float', 'name': 'maxY_'},
        '8': {'type': 'float', 'name': 'resolution_'}
        }, 'name': 'mapHeadInfo_'},
      '4': {'type': 'message', 'message_typedef': {
        '1': {'type': 'bytes', 'name': 'mapData_'}
        }, 'name': 'mapData_'},
      '5': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'mapHeadId_'},
        '2': {'type': 'bytes', 'name': 'mapName_'}
        }, 'name': 'mapInfo_'},
      '6': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'poseId_'},
        '2': {'type': 'message', 'message_typedef': {
          '1': {'type': 'int', 'name': 'update_'},
          '2': {'type': 'float', 'name': 'x_'},
          '3': {'type': 'float', 'name': 'y_'}
          }, 'name': ''} # error when using points_
        }, 'name': 'historyPose_'},
      '7': {'type': 'message', 'message_typedef': {
        '1': {'type': 'float', 'name': 'x_'},
        '2': {'type': 'float', 'name': 'y_'},
        '3': {'type': 'float', 'name': 'phi_'}
        }, 'name': 'chargeStation_'},
      '8': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'poseId_'},
        '2': {'type': 'int', 'name': 'update_'},
        '3': {'type': 'float', 'name': 'x_'},
        '4': {'type': 'float', 'name': 'y_'},
        '5': {'type': 'float', 'name': 'phi_'}
        }, 'name': 'currentPose_'},
      '11': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'pointId_'},
        '2': {'type': 'int', 'name': 'status_'},
        '3': {'type': 'int', 'name': 'pointType_'},
        '4': {'type': 'float', 'name': 'x_'},
        '5': {'type': 'float', 'name': 'y_'},
        '6': {'type': 'float', 'name': 'phi_'}
        }, 'name': 'navigationPoints_'},
      '12': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'roomId_'},
        '2': {'type': 'bytes', 'name': 'roomName_'},
        # '3': {'type': 'bytes', 'name': 'roomTypeId_'},
        # '4': {'type': 'bytes', 'name': 'meterialId_'},
        '5': {'type': 'int', 'name': 'cleanState_'},
        '6': {'type': 'int', 'name': 'roomClean_'},
        # '7': {'type': 'int', 'name': 'roomCleanIndex_'},
        '8': {'type': 'message', 'message_typedef': {
          '1': {'type': 'float', 'name': 'x_'},
          '2': {'type': 'float', 'name': 'y_'}
          }, 'name': 'roomNamePost_'}
        }, 'name': ''}, # error when using roomDataInfo_
      '13': {'type': 'message', 'message_typedef': {
        '1': {'type': 'bytes', 'name': 'matrix_'}
        }, 'name': 'roomMatrix_'},
      '14': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': 'room'},
        '2': {'type': 'message', 'message_typedef': {
          '1': {'type': 'int', 'name': 'x_'},
          '2': {'type': 'int', 'name': 'y_'},
          '3': {'type': 'int', 'name': 'value_'}
          }, 'name': ''} # error when using points_
        }, 'name': ''} # error when using roomChain_
      }

    def __init__(self, provider, vacuum):
        super(WyzeVacuum, self).__init__(provider, vacuum)

    @property
    def current_position(self):
        return self._get_property('current_position')

    @property
    def current_map(self):
        """
        This method returns a dictionary of map data after parsing the
        protobuf using the above definition.
        The map from the Wyze API is a zip-compressed base64-encoded
        blob of data, so we have to decode it, unzip it, then base64-
        encode it for parsing. Pain in the ass.
        :rtype: ``dict``
        :return: A dictionary of map properties
        """
        current_map = self._get_property('current_map')
        if 'map' in current_map:
            if isinstance(current_map['map'], str):
                current_map['map'] = self.parse_map(current_map['map'])
            return current_map['map']

        return current_map

    def parse_map(self, blob):
        import base64
        import binascii
        import blackboxprotobuf
        import json
        import zlib

        try:
            compressed = base64.b64decode(blob)
            if compressed is None:
                raise InvalidValueException('current_map', '')

            decompressed = zlib.decompress(compressed)

            # add the protobuf definition to the known types
            blackboxprotobuf.known_messages['robot_map'] = self._robot_map_proto
            
            # for some reason we have to re-encode and then re-decode the bytes
            map, typedef = blackboxprotobuf.protobuf_to_json(base64.b64decode(base64.b64encode(decompressed)), 'robot_map')

            return json.loads(map)
        except (binascii.Error, zlib.error):
                raise InvalidValueException('current_map', '')

    @property
    def rooms(self):
        if '12' in self.current_map:
            return [WyzeVacuumMapRoom(**room) for room in self.current_map['12']]

    @property
    def suction_level(self):
        return self._suction_levels.get(
            self._get_property('cleanlevel'),
            VacuumSuction.STANDARD)

    @suction_level.setter
    def suction_level(self, value: VacuumSuction):
        if value is not None:
            self._set_property('cleanlevel', value.code)
            self._provider.vacuum.set_suction_level(
                self.mac, self.model, self.suction_level.code)

    def _get_property(self, name, default=None):
        if name in self._device:
            return self._device[name]
        elif 'data' in self._device:
            if 'props' in self._device['data'] and name in self._device['data']['props']:
                return self._device['data']['props'][name]
            elif 'settings' in self._device['data'] and name in self._device['data']['settings']:
                return self._device['data']['settings'][name]
        elif 'props' in self._device and name in self._device['props']:
            return self._device['props'][name]
        elif 'settings' in self._device and name in self._device['settings']:
            return self._device['settings'][name]

        return default

    def _set_property(self, name, value):
        if name in self._device:
            self._device[name] = value
        elif 'data' in self._device:
            if 'props' in self._device['data'] and name in self._device['data']['props']:
                self._device['data']['props'][name] = value
            elif 'settings' in self._device['data'] and name in self._device['data']['settings']:
                self._device['data']['settings'][name] = value
        elif 'props' in self._device and name in self._device['props']:
            self._device['props'][name] = value
        elif 'settings' in self._device and name in self._device['settings']:
            self._device['settings'][name] = value

    @property
    def battery(self):
        return self._get_property('battary')

    @property
    def mode(self):
        return self._modes.get(self._get_property('mode'), VacuumMode.IDLE)

    @staticmethod
    def props():
        return {
            "iot_state": ("iot_state", "str"),
            "battary": ("battery", "int"),
            "mode": ("mode", "int"),
            "chargeState": ("charge_state", "int"),
            "cleanSize": ("clean_size", "int"),
            "cleanTime": ("clean_time", "int"),
            "fault_type": ("fault_type", "str"),
            "fault_code": ("fault_code", "int"),
            "current_mapid": ("current_mapid", "int"),
            "count": ("count", "int"),
            "cleanlevel": ("fan_speed", "int"),
            "notice_save_map": ("notice_save_map", "bool"),
            "memory_map_update_time": ("memory_map_update_time", "int"),
        }

    @staticmethod
    def clean_props():
        return {0: 1}

    @staticmethod
    def dock_props():
        return {3: 1}

    @staticmethod
    def pause_props():
        return {0: 2}

    @staticmethod
    def suction_level_props():
        return {
            'control_type': 1,
            'event_id': 'WRV_SETTINGS_SUCTION'
        }

    @staticmethod
    def device_info_props():
        return {
            "mac": ("mac", "str"),
            "ipaddr": ("ip", "str"),
            "device_type": ("device_type", "str"),
            "mcu_sys_version": ("mcu_sys_version", "str"),
        }

    @staticmethod
    def device_info_pids():
        return [pid for pid in WyzeVacuum.device_info_props().keys()]

    @staticmethod
    def pids():
        return [pid for pid in WyzeVacuum.props().keys()]

    @property
    def ip(self):
        return self._get_property('ipaddr')


class WyzeSensor(WyzeDevice, BaseSensor):

    def __init__(self, provider, sensor):
        super(BaseSensor, self).__init__(provider, sensor)

    @staticmethod
    def props():
        return {
            "power_state": ("P3", "int"),
            "available": ("P5", "int"),
            "rssi": ("P1303", "str"),
            "voltage": ("P1304", "str"),
        }


class WyzeContactSensor(WyzeSensor, BaseContactSensor):

    def __init__(self, provider, sensor):
        super(WyzeContactSensor, self).__init__(provider, sensor)

    @staticmethod
    def props():
        return WyzeSensor.props.update({
            "open_close_state": ("P1301", "str"),
            "rssi": ("P1304", "str"),
            "voltage": ("P1329", "str"),
        })


class WyzeMotionSensor(WyzeSensor, BaseMotionSensor):

    def __init__(self, provider, sensor):
        super(WyzeMotionSensor, self).__init__(provider, sensor)

    @staticmethod
    def props():
        return WyzeSensor.props.update({
            "motion_state": ("P1302", "str"),
            "rssi": ("P1304", "str"),
            "voltage": ("P1329", "str"),
        })
