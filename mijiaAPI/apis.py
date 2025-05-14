from typing import Union
import requests
import requests.cookies

from .code import ERROR_CODE
from .utils import defaultUA, post_data, PostDataError


class mijiaAPI(object):
    def __init__(self, auth_data: dict):
        if any(k not in auth_data for k in ['userId', 'deviceId', 'ssecurity', 'serviceToken']):
            raise Exception('Invalid authorize data')
        self.userId = auth_data['userId']
        self.ssecurity = auth_data['ssecurity']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': defaultUA,
            'x-xiaomi-protocal-flag-cli': 'PROTOCAL-HTTP2',
            'Cookie': f'PassportDeviceId={auth_data["deviceId"]};'
                      f'userId={auth_data["userId"]};'
                      f'serviceToken={auth_data["serviceToken"]};',
        })

    @staticmethod
    def _post_process(data: dict) -> Union[list, bool]:
        if data['code'] != 0:
            raise Exception(f'Failed to get data, {data["message"]}')
        return data['result']

    @property
    def available(self) -> bool:
        """check if the API is available"""
        uri = '/home/device_list'
        data = {"getVirtualModel": False, "getHuamiDevices": 0}
        try:
            post_data(self.session, self.ssecurity, uri, data)
            return True
        except PostDataError:
            return False

    def get_devices_list(self) -> dict:
        """get devices list
        mijiaAPI.get_devices_list() -> dict
        -------
        @return
        dict, devices list
        """
        uri = '/home/device_list'
        data = {"getVirtualModel": False, "getHuamiDevices": 0}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_homes_list(self) -> list:
        """get homes list
        mijiaAPI.get_homes_list() -> list
        -------
        @return
        list, homes list, including rooms
        """
        uri = '/v2/homeroom/gethome'
        data = {"fg": False, "fetch_share": True, "fetch_share_dev": True, "limit": 300, "app_ver": 7}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_scenes_list(self, home_id: str) -> list:
        """get scenes list
        set it in Mi Home APP -> Add -> Manual controls
        mijiaAPI.get_scenes_list(home_id: str) -> list
        -------
        @param
        home_id: str, room id, get from get_homes_list
        -------
        @return
        list, scenes list
        """
        uri = '/appgateway/miot/appsceneservice/AppSceneService/GetSceneList'
        data = {"home_id": home_id}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def run_scene(self, scene_id: str) -> bool:
        """run scene
        mijiaAPI.run_scene(scene_id: str) -> bool
        -------
        @param
        scene_id: str, scene id, get from get_scenes_list
        -------
        @return
        dict, result
        """
        uri = '/appgateway/miot/appsceneservice/AppSceneService/RunScene'
        data = {"scene_id": scene_id, "trigger_key": "user.click"}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_consumable_items(self, home_id: str) -> list:
        """get consumable items
        mijiaAPI.get_consumable_items(did: str) -> list
        -------
        @param
        home_id: str, room id, get from get_homes_list
        -------
        @return
        list, consumable items
        """
        uri = '/v2/home/standard_consumable_items'
        data = {"home_id": int(home_id), "owner_id": self.userId}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_devices_prop(self, data: list) -> list:
        """get devices properties
        mijiaAPI.get_devices_prop(data: list) -> list
        -------
        @param
        data: list of dict
            dict keys:
                - did: str, device id, get from get_devices_list
                - siid: str, service id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
                - piid: str, property id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
            model yeelink.light.lamp4 as an example:
            [
                {"did": "1234567890", "siid": 2, "piid": 2}, # get the brightness
                {"did": "1234567890", "siid": 2, "piid": 3}, # get the color temperature
            ]
        -------
        @return
        list, device properties
        """
        uri = '/miotspec/prop/get'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def set_devices_prop(self, data: list) -> list:
        """set devices properties
        mijiaAPI.set_devices_prop(data: list) -> list
        -------
        @param
        data: list of dict
            dict keys:
                - did: str, device id, get from get_devices_list
                - siid: str, service id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
                - piid: str, property id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
                - value: str, value to set
            model yeelink.light.lamp4 as an example:
            [
                {"did": "1234567890", "siid": 2, "piid": 2, "value": 50} # set the brightness to 50%
                {"did": "1234567890", "siid": 2, "piid": 3, "value": 2700} # set the color temperature to 2700K
            ]
        -------
        @return
        dict, result
        """
        uri = '/miotspec/prop/set'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def run_action(self, data: dict) -> dict:
        """run action
        mijiaAPI.run_action(data: dict) -> dict
        @param
        data: dict
            dict keys:
                - did: str, device id, get from get_devices_list
                - siid: str, service id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
                - aiid: str, action id, get from https://home.miot-spec.com/spec/{model}, model from get_devices_list
                - value: list, value to list
            model xiaomi.feeder.pi2001 as an example:
            {"did": "1234567890", "siid": 2, "aiid": 1, "value": [2]}, # Remote feeding (2 servings) of food
        -------
        @return
        dict, result
        """
        uri = '/miotspec/action'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))
