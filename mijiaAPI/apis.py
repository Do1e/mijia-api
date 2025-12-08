import json
import locale
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union
from urllib import parse

import requests
import tzlocal
from qrcode import QRCode

from .errors import ERROR_CODE, APIError, LoginError
from .logger import logger
from .miutils import (
    decrypt,
    gen_nonce,
    generate_enc_params,
    get_signed_nonce,
)


class mijiaAPI():
    def __init__(self, auth_data_path: Optional[str] = None):
        self.locale = locale.getlocale()[0] if locale.getlocale()[0] else "zh_CN"
        if '_' not in self.locale: # #57, make sure locale is in correct format
            self.locale = "zh_CN"
        self.api_base_url = "https://api.mijia.tech/app"
        self.login_url = "https://account.xiaomi.com/longPolling/loginUrl"
        self.service_login_url = f"https://account.xiaomi.com/pass/serviceLogin?_json=true&sid=mijia&_locale={self.locale}"

        if auth_data_path is None:
            self.auth_data_path = Path.home() / ".config" / "mijia-api" / "auth.json"
        elif Path(auth_data_path).is_dir():
            self.auth_data_path = Path(auth_data_path) / "auth.json"
        else:
            self.auth_data_path = Path(auth_data_path)

        if self.auth_data_path.exists():
            with open(self.auth_data_path, "r") as f:
                self.auth_data = json.load(f)
            self._init_session()
        else:
            self.auth_data = {}

    def _init_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "accept-encoding": "identity",
            "Content-Type": "application/x-www-form-urlencoded",
            "miot-accept-encoding": "GZIP",
            "miot-encrypt-algorithm": "ENCRYPT-RC4",
            "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2",
            "Cookie": f"cUserId={self.auth_data['cUserId']};"
                      f"yetAnotherServiceToken={self.auth_data['serviceToken']};"
                      f"serviceToken={self.auth_data['serviceToken']};"
                      f"timezone_id={tzlocal.get_localzone_name()};"
                      f"timezone=GMT{datetime.now().astimezone().strftime('%z')[:3]}:{datetime.now().astimezone().strftime('%z')[3:]};"
                      f"is_daylight={time.daylight};"
                      f"dst_offset={time.localtime().tm_isdst * 60 * 60 * 1000};"
                      f"channel=MI_APP_STORE;"
                      f"countryCode={self.locale.split('_')[1] if self.locale else 'CN'};"
                      f"PassportDeviceId={self.deviceId};"
                      f"locale={self.locale}",
        })

    @property
    def available(self) -> bool:
        if not self.auth_data:
            return False
        if any(key not in self.auth_data for key in ["ua", "ssecurity", "userId", "cUserId", "serviceToken"]):
            return False
        try:
            self.check_new_msg(refresh_token=False)
        except Exception:
            return False
        return True

    @property
    def pass_o(self) -> str:
        if "pass_o" in self.auth_data:
            return self.auth_data["pass_o"]
        self.auth_data["pass_o"] = "".join(random.choices("0123456789abcdef", k=16))
        return self.auth_data["pass_o"]

    @property
    def user_agent(self) -> str:
        if "ua" in self.auth_data:
            return self.auth_data["ua"]
        ua_id1 = "".join(random.choices("0123456789ABCDEF", k=40))
        ua_id2 = "".join(random.choices("0123456789ABCDEF", k=32))
        ua_id3 = "".join(random.choices("0123456789ABCDEF", k=32))
        ua_id4 = "".join(random.choices("0123456789ABCDEF", k=40))
        self.auth_data["ua"] = f"Android-15-11.0.701-Xiaomi-23046RP50C-OS2.0.212.0.VMYCNXM-" \
                               f"{ua_id1}-{self.locale.split('_')[1] if self.locale else 'CN'}-" \
                               f"{ua_id3}-{ua_id2}-SmartHome-MI_APP_STORE-{ua_id1}|{ua_id4}|{self.pass_o}-64"
        return self.auth_data["ua"]

    @property
    def deviceId(self) -> str:
        if "deviceId" in self.auth_data:
            return self.auth_data["deviceId"]
        self.auth_data["deviceId"] = "".join(random.choices("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-", k=16))
        return self.auth_data["deviceId"]

    def _parse_service_ret(self, service_ret: requests.Response) -> dict:
        text = service_ret.text.replace("&&&START&&&", "")
        service_data = json.loads(text)
        return service_data

    def _handle_ret(self, fetch_ret: requests.Response, verify_code: bool = True) -> dict:
        if fetch_ret.status_code != 200:
            raise LoginError(fetch_ret.status_code, fetch_ret.text)
        fetch_data = self._parse_service_ret(fetch_ret)
        if verify_code and fetch_data.get("code", 0) != 0:
            raise LoginError(fetch_data["code"], fetch_data.get("desc", "未知错误"))
        return fetch_data

    @staticmethod
    def _print_qr(loginurl: str, box_size: int = 10):
        logger.info("请使用米家APP扫描下方二维码")
        qr = QRCode(border=1, box_size=box_size)
        qr.add_data(loginurl)
        try:
            qr.print_ascii(invert=True, tty=True)
        except OSError:
            qr.print_ascii(invert=True, tty=False)
            logger.info("如果无法扫描二维码，"
                        "请更改终端字体，"
                        "如`Maple Mono`、`Fira Code`等。")

    def _save_auth_data(self):
        self.auth_data["saveTime"] = int(time.time() * 1000)
        self.auth_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.auth_data_path, "w") as f:
            json.dump(self.auth_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"已保存认证数据到 {self.auth_data_path}")
        logger.debug(f"认证数据: {self.auth_data}")

    def _get_location(self) -> dict:
        headers = {
            "User-Agent": self.user_agent,
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"deviceId={self.deviceId};"
                      f"pass_o={self.pass_o};"
                      f"passToken={self.auth_data.get('passToken', '')};"
                      f"userId={self.auth_data.get('userId', '')};"
                      f"cUserId={self.auth_data.get('cUserId', '')};"
                      f"uLocale={self.locale};"
        }
        service_ret = requests.get(self.service_login_url, headers=headers)
        service_data = self._handle_ret(service_ret, verify_code=False)
        location = service_data["location"]
        if service_data['code'] == 0:
            ret = self.session.get(location)
            if ret.status_code == 200 and ret.text == "ok":
                cookies = self.session.cookies.get_dict()
                self.auth_data.update(cookies)
                self.auth_data["ssecurity"] = service_data["ssecurity"]
                return {"code": 0, "message": "刷新Token成功"}
        location_data = parse.parse_qs(parse.urlparse(location).query)
        return {k: v[0] for k, v in location_data.items()}

    def _refresh_token(self) -> dict:
        if self.available:
            logger.debug("Token 有效，无需刷新")
            return self.auth_data
        location_data = self._get_location()
        if location_data.get("code", -1) == 0 and location_data.get("message", "") == "刷新Token成功":
            self._save_auth_data()
            self._init_session()
            logger.debug("刷新Token成功")
            return self.auth_data
        else:
            raise LoginError(-1, "刷新Token失败，请重新登录")

    def login(self, *args, **kwargs) -> dict:
        """
        二维码登录方法

        通过米家账号二维码登录，使用米家APP扫描二维码完成身份验证。
        如果Token有效，会直接返回保存的认证数据而不需要重新登录。

        参数:
            无

        返回值:
            dict: 包含认证信息的字典，包括以下关键字段: ["psecurity", "nonce", "ssecurity", "passToken", "userId", "cUserId", "serviceToken", "expireTime", ...]

        异常:
            LoginError: 当登录超时或服务器返回错误时抛出
        """
        return self.QRlogin()

    def QRlogin(self) -> dict:
        """
        二维码登录方法

        通过米家账号二维码登录，使用米家APP扫描二维码完成身份验证。
        如果Token有效，会直接返回并保存认证数据。

        参数:
            无

        返回值:
            dict: 包含认证信息的字典，包括以下关键字段: ["psecurity", "nonce", "ssecurity", "passToken", "userId", "cUserId", "serviceToken", "expireTime", ...]

        异常:
            LoginError: 当登录超时或服务器返回错误时抛出
        """
        # Step 1: 从 serviceLogin 获取登录链接参数
        location_data = self._get_location()
        if location_data.get("code", -1) == 0 and location_data.get("message", "") == "刷新Token成功":
            self._save_auth_data()
            self._init_session()
            logger.info("刷新Token成功，无需登录")
            return self.auth_data

        # Step 2: 获取并打印二维码
        location_data.update({
            "theme": "",
            "bizDeviceType": "",
            "_hasLogo": "false",
            "_qrsize": "240",
            "_dc": str(int(time.time() * 1000)),
        })
        url = self.login_url + "?" + parse.urlencode(location_data)
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }
        login_ret = requests.get(url, headers=headers)
        login_data = self._handle_ret(login_ret)
        self._print_qr(login_data["loginUrl"])
        print(f"也可以访问链接查看二维码图片: {login_data['qr']}")

        # Step 3: 轮询等待扫码登录
        session = requests.Session()
        try:
            lp_ret = session.get(login_data["lp"], headers=headers, timeout=120)
            lp_data = self._handle_ret(lp_ret)
        except requests.exceptions.Timeout:
            raise LoginError(-1, "超时，请重试")

        # Step 4: 处理登录结果
        auth_keys = ["psecurity", "nonce", "ssecurity", "passToken", "userId", "cUserId"]
        for key in auth_keys:
            self.auth_data[key] = lp_data[key]
        callback_url = lp_data["location"]
        session.get(callback_url, headers=headers)
        cookies = session.cookies.get_dict()
        self.auth_data.update(cookies)
        self.auth_data.update({
            "expireTime": int((datetime.now() + timedelta(days=30)).timestamp() * 1000),
        })
        self._save_auth_data()
        logger.info("登录成功")
        self._init_session()
        return self.auth_data


    def _request(self, uri: str, data: dict, refresh_token: bool = True) -> dict:
        logger.debug(f"请求 URI: {uri}，数据: {data}")
        if refresh_token:
            self._refresh_token()
        url = self.api_base_url + uri
        params = { "data": json.dumps(data, separators=(',', ':')) }
        nonce = gen_nonce()
        signed_nonce = get_signed_nonce(self.auth_data["ssecurity"], nonce)
        params = generate_enc_params(uri, "POST", signed_nonce, nonce, params, self.auth_data["ssecurity"])
        ret = self.session.post(url, data=params)
        try:
            ret_data = json.loads(ret.text)
        except json.JSONDecodeError:
            dec_data = decrypt(self.auth_data["ssecurity"], nonce, ret.text)
            ret_data = json.loads(dec_data)
        logger.debug(f"响应数据: {ret_data}")
        if ret_data.get("code", 0) != 0 or "result" not in ret_data:
            raise APIError(ret_data["code"], ret_data.get("message", ret_data.get("desc", "未知错误")))
        return ret_data["result"]

    @staticmethod
    def _add_home_id(data: Union[list, dict], home_id: str) -> Union[list, dict]:
        if isinstance(data, list):
            for item in data:
                item.update({"home_id": home_id})
            return data
        elif isinstance(data, dict):
            data.update({"home_id": home_id})
            return data
        return data


    def _get_home_owner(self, home_id: str) -> int:
        homes = self.get_homes_list()
        for home in homes:
            if home["id"] == home_id:
                return int(home["uid"])
        raise APIError(-1, f"未找到 home_id={home_id} 的家庭信息")

    def _get_devices_list(self, home_id: str) -> list:
        uri = "/home/home_device_list"
        start_did = ""
        has_more = True
        devices = []
        while has_more:
            data = {
                "home_owner": self._get_home_owner(home_id),
                "home_id": int(home_id),
                "limit": 200,
                "start_did": start_did,
                "get_split_device": True,
                "support_smart_home": True,
                "get_cariot_device": True,
                "get_third_device": True
            }
            ret = self._request(uri, data)
            if ret and ret.get("device_info"):
                devices.extend(ret["device_info"])
                start_did = ret.get("max_did", "")
                has_more = ret.get("has_more", False) and start_did != ""
            else:
                has_more = False
        return self._add_home_id(devices, home_id)

    def _get_scenes_list(self, home_id: str) -> list:
        uri = "/appgateway/miot/appsceneservice/AppSceneService/GetSimpleSceneList"
        data = {"app_version": 12, "get_type": 2, "home_id": str(home_id), "owner_uid": self._get_home_owner(home_id)}
        ret = self._request(uri, data)
        if ret and "manual_scene_info_list" in ret:
            scenes = ret["manual_scene_info_list"]
            return self._add_home_id(scenes, home_id)
        return []

    def _get_consumable_items(self, home_id: str) -> list:
        uri = "/v2/home/standard_consumable_items"
        data = {"home_id": int(home_id), "owner_id": self._get_home_owner(home_id), "filter_ignore": True}
        ret = self._request(uri, data)
        try:
            items = ret["items"][0]["consumes_data"]
            for item in items:
                if isinstance(item.get("details"), list) and len(item["details"]) == 1:
                    item["details"] = item["details"][0]
            return self._add_home_id(items, home_id)
        except (KeyError, IndexError):
            return []


    def check_new_msg(self, begin_at: int = int(time.time()) - 3600, refresh_token: bool = True) -> dict:
        uri = "/v2/message/v2/check_new_msg"
        data = {"begin_at": begin_at}
        return self._request(uri, data, refresh_token=refresh_token)

    def get_homes_list(self) -> list:
        """
        获取用户的所有家庭列表

        包括自己创建的家庭和被共享的家庭。

        参数:
            无

        返回值:
            list: 家庭信息列表，每个元素为一个dict，包含以下常见字段：
                - id (str): 家庭ID
                - name (str): 家庭名称
                - uid (int): 家庭所属用户ID
                - roomlist (list): 家庭房间列表
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        uri = "/v2/homeroom/gethome_merged"
        data = {"fg": True, "fetch_share": True, "fetch_share_dev": True, "fetch_cariot": True, "limit": 300, "app_ver": 7, "plat_form": 0}
        return self._request(uri, data)["homelist"]

    def get_devices_list(self, home_id: Optional[str] = None) -> list:
        """
        获取设备列表

        获取用户指定家庭中的所有设备，或者获取所有家庭中的所有设备。

        参数:
            home_id (Optional[str]): 可选，家庭ID。
                - 如果为 None，则获取所有家庭中的所有设备
                - 如果指定，则仅获取该家庭中的设备

        返回值:
            list: 设备信息列表，每个元素为一个dict，包含以下常见字段：
                - did (str): 设备ID
                - name (str): 设备名称
                - model (str): 设备型号
                - uid (int): 设备所属用户ID
                - home_id (str): 设备所属家庭ID
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        if home_id is None:
            home_list = self.get_homes_list()
            devices = []
            for home in home_list:
                devices.extend(self._get_devices_list(home["id"]))
            return devices
        else:
            return self._get_devices_list(home_id)

    def get_shared_devices_list(self) -> list:
        """
        获取共享设备列表

        获取用户被共享的所有设备列表。

        参数:
            无

        返回值:
            list: 共享设备信息列表，每个元素为一个dict，包含以下常见字段：
                - did (str): 设备ID
                - name (str): 设备名称
                - model (str): 设备型号
                - uid (int): 设备所属用户ID
                - ...
        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        uri = "/v2/home/device_list_page"
        data = {"ssid": "<unknown ssid>", "bssid": "02:00:00:00:00:00", "getVirtualModel": True, "getHuamiDevices": 1, "get_split_device": True, "support_smart_home": True, "get_cariot_device": True, "get_third_device": True, "get_phone_device": True, "get_miwear_device": True}
        ret = self._request(uri, data)
        devices = [item for item in ret["list"] if item.get("owner", False)]
        for device in devices:
            device.update({"home_id": "shared"})
        return devices

    def get_scenes_list(self, home_id: Optional[str] = None) -> list:
        """
        获取场景列表

        获取用户指定家庭中的所有手动场景，或者获取所有家庭中的所有手动场景。

        参数:
            home_id (Optional[str]): 可选，家庭ID。
                - 如果为 None，则获取所有家庭中的所有场景
                - 如果指定，则仅获取该家庭中的场景

        返回值:
            list: 场景信息列表，每个元素为一个dict，包含以下常见字段：
                - scene_id (str): 场景ID
                - name (str): 场景名称
                - home_id (str): 场景所属家庭ID
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        if home_id is None:
            home_list = self.get_homes_list()
            scenes = []
            for home in home_list:
                scenes.extend(self._get_scenes_list(home["id"]))
            return scenes
        else:
            return self._get_scenes_list(home_id)

    def run_scene(self, scene_id: str, home_id: str) -> bool:
        """
        执行手动场景

        触发指定的米家手动场景，可在 米家APP->智能->+->手动控制 中添加。

        参数:
            scene_id (str): 场景ID，从 get_scenes_list() 获取的场景的 scene_id 字段
            home_id (str): 家庭ID，场景所属的家庭ID

        返回值:
            bool: 场景执行结果
                - True 表示场景执行成功
                - False 表示场景执行失败

        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        uri = "/appgateway/miot/appsceneservice/AppSceneService/NewRunScene"
        data = {"scene_id": scene_id, "scene_type": 2, "phone_id": "null", "home_id": str(home_id), "owner_uid": self._get_home_owner(home_id)}
        return self._request(uri, data)

    def get_consumable_items(self, home_id: Optional[str] = None) -> list:
        """
        获取耗材列表

        获取用户指定家庭中的所有耗材信息（如滤芯、电池等需要更换的配件），
        或者获取所有家庭中的所有耗材信息。

        参数:
            home_id (Optional[str]): 可选，家庭ID。
                - 如果为 None，则获取所有家庭中的所有耗材
                - 如果指定，则仅获取该家庭中的耗材

        返回值:
            list: 耗材信息列表，每个元素为一个dict，包含以下常见字段：
                - did (str): 耗材所属设备ID
                - name (str): 耗材所属设备名称
                - home_id (str): 耗材所属家庭ID
                - details (dict): 耗材详情，包含以下常见字段：
                    - id (str): 耗材ID
                    - description (str): 耗材描述
                    - value (str): 耗材当前值
                    - consumable_type (str): 耗材类型
                    - ...
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出
        """
        if home_id is None:
            home_list = self.get_homes_list()
            items = []
            for home in home_list:
                items.extend(self._get_consumable_items(home["id"]))
            return items
        else:
            return self._get_consumable_items(home_id)

    def get_devices_prop(self, data: Union[list, dict]) -> Union[list, dict]:
        """
        获取设备属性

        获取一个或多个设备的属性值，例如灯的亮度、色温、开关状态等。
        支持批量获取多个设备的多个属性。

        参数:
            data (Union[list, dict]): 设备属性查询参数
                - 如果为 dict，则获取单个设备的单个或多个属性
                - 如果为 list，则获取多个设备的属性

                dict/list 中每个元素的格式：
                - did (str): 设备ID，从 get_devices_list() 获取
                - siid (int): 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取
                - piid (int): 属性ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取

        返回值:
            Union[list, dict]: 设备属性查询结果
                - 如果输入为 dict，返回单个设备的属性结果 dict
                - 如果输入为 list，返回属性结果列表

                返回的 dict 包含以下字段：
                - did (str): 设备ID
                - siid (int): 服务ID
                - piid (int): 属性ID
                - value: 属性值，数据类型根据属性定义而定
                - code (int): 错误代码，0 表示成功
                - updateTime (int): 属性最后更新时间的时间戳（秒）
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出

        示例:
            # yeelink.light.lamp4 (米家台灯 1S)
            # 单个属性查询
            >>> result = api.get_devices_prop({
            ...     "did": "1234567890",
            ...     "siid": 2,
            ...     "piid": 1
            ... })  # 获取灯的开关状态

            # 批量查询
            >>> result = api.get_devices_prop([
            ...     {"did": "1234567890", "siid": 2, "piid": 2},  # 亮度
            ...     {"did": "1234567890", "siid": 2, "piid": 3},  # 色温
            ...     {"did": "0987654321", "siid": 2, "piid": 1}   # 另一个灯的开关
            ... ])
        """
        if isinstance(data, dict):
            params = [data]
        else:
            params = data
        uri = "/miotspec/prop/get"
        ret_data = self._request(uri, {"params": params, "datasource": 1})
        if isinstance(data, dict) and len(ret_data) == 1:
            return ret_data[0]
        return ret_data

    def set_devices_prop(self, data: Union[list, dict]) -> Union[list, dict]:
        """
        设置设备属性

        设置一个或多个设备的属性值，例如灯的亮度、色温等。
        支持批量设置多个设备的多个属性。

        参数:
            data (Union[list, dict]): 设备属性参数
                - 如果为 dict，则设置单个设备的单个或多个属性
                - 如果为 list，则设置多个设备的属性

                dict/list 中每个元素的格式：
                - did (str): 设备ID，从 get_devices_list() 获取
                - siid (int): 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取
                - piid (int): 属性ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取
                - value: 要设置的值，数据类型根据属性定义而定

        返回值:
            Union[list, dict]: 设置结果
                - 如果输入为 dict，返回单个设备的设置结果 dict
                - 如果输入为 list，返回设置结果列表

                返回的 dict 包含以下字段：
                - did (str): 设备ID
                - siid (int): 服务ID
                - piid (int): 属性ID
                - code (int): 错误代码，0 表示成功
                - message (str): 执行结果描述
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出

        示例:
            # yeelink.light.lamp4 (米家台灯 1S)
            # 单个属性设置
            >>> result = api.set_devices_prop({
            ...     "did": "1234567890",
            ...     "siid": 2,
            ...     "piid": 1,
            ...     "value": True
            ... }) # 开灯

            # 批量设置
            >>> result = api.set_devices_prop([
            ...     {"did": "1234567890", "siid": 2, "piid": 2, "value": 50},    # 设置亮度为50%
            ...     {"did": "1234567890", "siid": 2, "piid": 3, "value": 2700},  # 设置色温为2700K
            ...     {"did": "0987654321", "siid": 2, "piid": 1, "value": True}   # 开另一个灯
            ... ])
        """
        if isinstance(data, dict):
            params = [data]
        else:
            params = data
        uri = "/miotspec/prop/set"
        ret_data = self._request(uri, {"params": params})
        for ret in ret_data:
            if ret.get("code", 0) != 0:
                ret.update({"message": ERROR_CODE.get(str(ret["code"]), "未知错误")})
            else:
                ret.update({"message": "成功"})
        if isinstance(data, dict) and len(ret_data) == 1:
            return ret_data[0]
        return ret_data

    def run_action(self, data: Union[list, dict]) -> Union[list, dict]:
        """
        执行设备操作

        执行一个或多个设备的操作/方法，例如开关灯、喂食等。
        支持批量执行多个设备的多个操作。

        参数:
            data (Union[list, dict]): 设备操作参数
                - 如果为 dict，则执行单个设备的操作
                - 如果为 list，则执行多个设备的操作

                dict/list 中每个元素的格式：
                - did (str): 设备ID，从 get_devices_list() 获取
                - siid (int): 服务ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取
                - aiid (int): 操作/方法ID，从 https://home.miot-spec.com/spec/{model} 获取，
                              model 从 get_devices_list() 获取
                - value (list): 可选，操作的参数列表，根据具体操作定义而定

        返回值:
            Union[list, dict]: 操作结果
                - 如果输入为 dict，返回单个设备的操作结果 dict
                - 如果输入为 list，返回操作结果列表

                返回的 dict 包含以下字段：
                - did (str): 设备ID
                - siid (int): 服务ID
                - aiid (int): 操作/方法ID
                - code (int): 错误代码，0 表示成功
                - message (str): 执行结果描述
                - ...

        异常:
            APIError: 当API请求失败或返回错误时抛出

        示例:
            # yeelink.light.lamp4 (米家台灯 1S)
            >>> result = api.run_action({
            ...     "did": "1234567890",
            ...     "siid": 2,
            ...     "aiid": 1
            ... })  # 开/关灯

            # xiaomi.feeder.pi2001 (米家智能宠物喂食器2)
            >>> result = api.run_action({
            ...     "did": "0987654321",
            ...     "siid": 2,
            ...     "aiid": 1,
            ...     "value": [2]  # 喂食2份
            ... })

            # 批量操作
            >>> result = api.run_action([
            ...     {"did": "1234567890", "siid": 2, "aiid": 1},
            ...     {"did": "0987654321", "siid": 2, "aiid": 1, "value": [1]}
            ... ])
        """
        if isinstance(data, dict):
            params = [data]
        else:
            params = data
        uri = "/miotspec/action"
        ret_data = []
        for param in params:
            ret = self._request(uri, {"params": param})
            ret_data.append(ret)
        for ret in ret_data:
            if ret.get("code", 0) != 0:
                ret.update({"message": ERROR_CODE.get(str(ret["code"]), "未知错误")})
            else:
                ret.update({"message": "成功"})
        if isinstance(data, dict) and len(ret_data) == 1:
            return ret_data[0]
        return ret_data

    def get_statistics(self, data: dict) -> list:
        """
        获取设备统计数据。

        获取指定设备的统计信息，如耗电量、使用时长等。支持按小时、天、周、月等不同粒度统计。

        参数：
            data (dict): 统计查询参数，包含以下字段：
                - did (str): 设备ID
                - key (str): 统计数据的键，格式为 siid.piid（服务ID.属性ID），
                  例如 "7.1" 表示 lumi.acpartner.mcn04 (米家空调伴侣Pro 万能遥控版) 的 power-consumption
                - data_type (str): 统计数据类型，可选值：
                  * stat_hour_v3: 按小时统计
                  * stat_day_v3: 按天统计
                  * stat_week_v3: 按周统计
                  * stat_month_v3: 按月统计（较新设备）
                  注：较旧设备使用的数据类型不含 "_v3" 后缀
                - limit (int): 返回的最大条目数
                - time_start (int): 开始时间戳（秒）
                - time_end (int): 结束时间戳（秒）

        返回值：
            list: 统计数据列表，每项包含以下字段：
                - value (str): 统计值（通常需要用 eval() 解析）
                - time (int): 时间戳

        已知问题：
            - 支持的设备有限，不同型号设备的 API 可能不同
            - 较旧的设备 data_type 格式不同（无 "_v3" 后缀）
            - 不同设备的 key 值不同，例如 lumi.acpartner.mcn02 的 key 为 "powerCost"
            - 详见 https://github.com/Do1e/mijia-api/issues/46

        参考文档：
            https://iot.mi.com/new/doc/accesses/direct-access/extension-development/extension-functions/statistical-interface

        示例：
            获取 lumi.acpartner.mcn04 (米家空调伴侣Pro 万能遥控版) 过去6个月的月度耗电量统计：

            >>> import time
            >>> from mijiaAPI import mijiaAPI
            >>> api = mijiaAPI(".mijia-api-data/auth.json")
            >>> ret = api.get_statistics({
            ...     "did": "123456",
            ...     "key": "7.1",
            ...     "data_type": "stat_month_v3",
            ...     "limit": 6,
            ...     "time_start": int(time.time() - 24 * 3600 * 30 * 6),
            ...     "time_end": int(time.time()),
            ... })
            >>> for item in ret:
            ...     value = eval(item['value'])[0]
            ...     ts = item['time']
            ...     date = time.strftime('%Y-%m-%d', time.localtime(ts))
            ...     print(f'{date}: {value}')
        """
        if isinstance(data, dict):
            params = [data]
        else:
            params = data
        uri = "/v2/user/statistics"
        ret_data = []
        for param in params:
            ret = self._request(uri, param)
            ret_data.append(ret)
        if isinstance(data, dict) and len(ret_data) == 1:
            return ret_data[0]
        return ret_data
