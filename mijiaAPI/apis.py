from datetime import datetime
from typing import Union

import requests
import requests.cookies

from .utils import defaultUA, post_data, PostDataError


class mijiaAPI(object):
    def __init__(self, auth_data: dict):
        """
        初始化mijiaAPI对象。

        Args:
            auth_data (dict): 包含授权信息的字典，必须包含'userId'、'deviceId'、'ssecurity'和'serviceToken'。

        Raises:
            Exception: 当授权数据不完整时抛出异常。
        """
        if any(k not in auth_data for k in ['userId', 'deviceId', 'ssecurity', 'serviceToken']):
            raise Exception('Invalid authorize data')
        self.userId = auth_data['userId']
        self.ssecurity = auth_data['ssecurity']
        self.session = requests.Session()
        self.expireTime = auth_data.get('expireTime', None)
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
        """
        检查API是否可用。

        Returns:
            bool: API可用返回True，否则返回False。
        """
        if self.expireTime:
            expire_time = datetime.strptime(self.expireTime, '%Y-%m-%d %H:%M:%S')
            if expire_time < datetime.now():
                return False
            return True
        return False

    def get_devices_list(self) -> dict:
        """
        获取设备列表。

        Returns:
            dict: 设备列表。
        """
        uri = '/home/device_list'
        data = {"getVirtualModel": False, "getHuamiDevices": 0}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_homes_list(self) -> list:
        """
        获取家庭列表。

        Returns:
            list: 家庭列表，包括房间信息。
        """
        uri = '/v2/homeroom/gethome'
        data = {"fg": False, "fetch_share": True, "fetch_share_dev": True, "limit": 300, "app_ver": 7}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_scenes_list(self, home_id: str) -> list:
        """
        获取场景列表。

        在米家APP中通过"添加 -> 手动控制"设置。

        Args:
            home_id (str): 家庭ID，从get_homes_list获取。

        Returns:
            list: 场景列表。
        """
        uri = '/appgateway/miot/appsceneservice/AppSceneService/GetSceneList'
        data = {"home_id": home_id}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def run_scene(self, scene_id: str) -> bool:
        """
        运行场景。

        Args:
            scene_id (str): 场景ID，从get_scenes_list获取。

        Returns:
            bool: 操作结果。
        """
        uri = '/appgateway/miot/appsceneservice/AppSceneService/RunScene'
        data = {"scene_id": scene_id, "trigger_key": "user.click"}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_consumable_items(self, home_id: str) -> list:
        """
        获取耗材列表。

        Args:
            home_id (str): 家庭ID，从get_homes_list获取。

        Returns:
            list: 耗材列表。
        """
        uri = '/v2/home/standard_consumable_items'
        data = {"home_id": int(home_id), "owner_id": self.userId}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def get_devices_prop(self, data: list) -> list:
        """
        获取设备属性。

        Args:
            data (list): 设备属性请求列表，每项为包含以下键的字典：
                - did: 设备ID，从get_devices_list获取
                - siid: 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取
                - piid: 属性ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取

                示例(yeelink.light.lamp4)：
                [
                    {"did": "1234567890", "siid": 2, "piid": 2}, # 获取亮度
                    {"did": "1234567890", "siid": 2, "piid": 3}, # 获取色温
                ]

        Returns:
            list: 设备属性信息列表。
        """
        uri = '/miotspec/prop/get'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def set_devices_prop(self, data: list) -> list:
        """
        设置设备属性。

        Args:
            data (list): 设备属性设置列表，每项为包含以下键的字典：
                - did: 设备ID，从get_devices_list获取
                - siid: 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取
                - piid: 属性ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取
                - value: 要设置的值

                示例(yeelink.light.lamp4)：
                [
                    {"did": "1234567890", "siid": 2, "piid": 2, "value": 50} # 设置亮度为50%
                    {"did": "1234567890", "siid": 2, "piid": 3, "value": 2700} # 设置色温为2700K
                ]

        Returns:
            list: 操作结果。
        """
        uri = '/miotspec/prop/set'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))

    def run_action(self, data: dict) -> dict:
        """
        执行设备动作。

        Args:
            data (dict): 动作请求，包含以下键：
                - did: 设备ID，从get_devices_list获取
                - siid: 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取
                - aiid: 动作ID，从 https://home.miot-spec.com/spec/{model} 获取，model从get_devices_list获取
                - value: 参数列表

                示例(xiaomi.feeder.pi2001)：
                {"did": "1234567890", "siid": 2, "aiid": 1, "value": [2]}, # 远程喂食2份

        Returns:
            dict: 操作结果。
        """
        uri = '/miotspec/action'
        data = {"params": data}
        return self._post_process(post_data(self.session, self.ssecurity, uri, data))
