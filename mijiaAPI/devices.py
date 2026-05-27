import json
import re
import time
from pathlib import Path
from typing import Optional, Union

import requests

from .apis import mijiaAPI
from .errors import (
    DeviceActionError,
    DeviceGetError,
    DeviceNotFoundError,
    DeviceSetError,
    GetDeviceInfoError,
    MultipleDevicesFoundError,
)
from .logger import logger
from .version import version


device_url = "https://home.miot-spec.com/spec/"


class DevProp():
    def __init__(self, prop_dict: dict):
        self.name = prop_dict["name"]
        self.desc = prop_dict["description"]
        self.type = prop_dict["type"]
        if self.type not in ["bool", "int", "uint", "float", "string"]:
            raise ValueError(f"不支持的类型: {self.type}, 可选类型: bool, int, uint, float, string")
        self.rw = prop_dict["rw"]
        self.range = prop_dict["range"]
        self.value_list = prop_dict.get("value-list", None)
        self.method = prop_dict["method"]

    def __str__(self):
        lines = [
            f"  {self.name}: {self.desc}",
            f"    valuetype: {self.type}, rw: {self.rw}, range: {self.range}"
        ]

        if self.value_list:
            value_lines = [f"    {item['value']}: {item['description']}" for item in self.value_list]
            lines.extend(value_lines)

        return "\n".join(lines)


class DevAction():
    def __init__(self, act_dict: dict):
        self.name = act_dict["name"]
        self.desc = act_dict["description"]
        self.method = act_dict["method"]

    def __str__(self):
        return f"  {self.name}: {self.desc}"


class mijiaDevice():
    def __init__(
            self,
            api: mijiaAPI,
            did: Optional[str] = None,
            dev_name: Optional[str] = None,
            sleep_time: float = 0.5,
    ):
        self.api = api

        if did is None and dev_name is None:
            raise ValueError("必须提供 did 或 dev_name 参数之一")
        if did is not None and dev_name is not None:
            logger.warning("同时提供了 did 和 dev_name 参数，将忽略 dev_name")

        devices_list = self.api.get_devices_list()
        if did is None:
            matches = [device for device in devices_list if device["name"] == dev_name]
            if not matches:
                raise DeviceNotFoundError(dev_name)
            else:
                if len(matches) > 1:
                    raise MultipleDevicesFoundError(f"找到多个 dev_name 为 '{dev_name}' 的设备，请使用 did 参数指定具体设备或者修改设备名称以区分")
                did = matches[0]["did"]
                model = matches[0]["model"]
        else:
            matches = [device for device in devices_list if device["did"] == did]
            if not matches:
                raise DeviceNotFoundError(did)
            else:
                if len(matches) > 1:
                    raise MultipleDevicesFoundError(f"找到多个 did 为 '{did}' 的设备，未预想的问题，欢迎提交 issue: https://github.com/Do1e/mijia-api/issues")
                dev_name = matches[0].get("name", None)
                model = matches[0]["model"]

        dev_info = get_device_info(model, cache_path=api.auth_data_path.parent)
        self.did = did
        self.model = model
        self.name = dev_name if dev_name is not None else dev_info["name"]
        self.sleep_time = sleep_time

        self.prop_list = {}
        for prop in dev_info.get("properties", []):
            prop_obj = DevProp(prop)
            name = prop["name"]
            self.prop_list[name] = prop_obj
            if "-" in name:
                self.prop_list[name.replace("-", "_")] = prop_obj

        self.action_list = {
            act["name"]: DevAction(act)
            for act in dev_info.get("actions", [])
        }

    def __str__(self) -> str:
        prop_list_str = "\n".join(filter(None, (str(v) for k, v in self.prop_list.items() if "_" not in k)))
        action_list_str = "\n".join(map(str, self.action_list.values()))
        return (f"{self.name} ({self.model})\n"
                f"Properties:\n{prop_list_str if prop_list_str else 'No properties available'}\n"
                f"Actions:\n{action_list_str if action_list_str else 'No actions available'}")


    def get(self, name: str) -> Union[bool, int, float, str]:
        if name not in self.prop_list:
            raise ValueError(f"不支持的属性: {name}, 可用属性: {list(self.prop_list.keys())}")
        prop = self.prop_list[name]
        if "r" not in prop.rw:
            raise ValueError(f"属性 {name} 不可读取")
        method = prop.method.copy()
        method["did"] = self.did
        result = self.api.get_devices_prop(method)
        if result["code"] != 0:
            raise DeviceGetError(self.name, name, result["code"])
        time.sleep(self.sleep_time)
        logger.debug(f"获取属性: {self.name} -> {name}, 结果: {result}")
        return result["value"]

    def set(self, name: str, value: Union[bool, int, float, str]):
        if name not in self.prop_list:
            raise ValueError(f"不支持的属性: {name}, 可用属性: {list(self.prop_list.keys())}")
        prop = self.prop_list[name]
        if "w" not in prop.rw:
            raise ValueError(f"属性 {name} 不可写入")
        if prop.type == "bool":
            if isinstance(value, str):
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value in ["0", "1"]:
                    value = bool(int(value))
                else:
                    raise ValueError(f"无效布尔值: {value}")
            elif isinstance(value, int):
                if value == 0:
                    value = False
                elif value == 1:
                    value = True
                else:
                    raise ValueError(f"无效布尔值: {value}")
            elif not isinstance(value, bool):
                raise ValueError(f"无效布尔值: {value}")
        elif prop.type in ["int", "uint"]:
            value = int(value)
            if prop.range:
                if value < prop.range[0] or value > prop.range[1]:
                    raise ValueError(f"{value} 超出数值范围, 应该在 {prop.range[:2]} 之间")
                if len(prop.range) >= 3 and prop.range[2] != 1:
                    if (value - prop.range[0]) % prop.range[2] != 0:
                        raise ValueError(
                            f"无效的值: {value}, 应该在范围 {prop.range[:2]} 内且步长为 {prop.range[2]}")
        elif prop.type == "float":
            value = float(value)
            if prop.range:
                if value < prop.range[0] or value > prop.range[1]:
                    raise ValueError(f"{value} 超出数值范围, 应该在 {prop.range[:2]} 之间")
                if len(prop.range) >= 3 and isinstance(prop.range[2], int):
                    if int(value - prop.range[0]) % prop.range[2] != 0:
                        raise ValueError(
                            f"无效的值: {value}, 应该在范围 {prop.range[:2]} 内且步长为 {prop.range[2]}")
        elif prop.type == "string":
            if not isinstance(value, str):
                raise ValueError(f"无效字符串值: {value}")
        else:
            raise ValueError(f"不支持的类型: {prop.type}, 可用类型: bool, int, uint, float, string")
        if prop.value_list:
            if value not in [item["value"] for item in prop.value_list]:
                raise ValueError(f"无效值: {value}, 请使用 {prop.value_list}")
        method = prop.method.copy()
        method["did"] = self.did
        method["value"] = value
        result = self.api.set_devices_prop(method)
        if result["code"] == 1:
            logger.warning(f"网关已经接收指令，无法判断是否设置成功: {self.name} -> {name}, 值: {value}")
        elif result["code"] != 0:
            raise DeviceSetError(self.name, name, result["code"])
        time.sleep(self.sleep_time)
        logger.debug(f"设置属性: {self.name} -> {name}, 值: {value}, 结果: {result}")

    def __getattr__(self, name: str) -> Union[bool, int, float, str]:
        if "prop_list" in self.__dict__ and name in self.prop_list:
            return self.get(name)
        else:
            return super().__getattr__(name)

    def __setattr__(self, name: str, value: Union[bool, int, float, str]) -> None:
        if "prop_list" in self.__dict__ and name in self.prop_list:
            self.set(name, value)
        else:
            super().__setattr__(name, value)

    def run_action(
            self,
            name: str,
            value: Optional[Union[list, tuple]] = None,
            **kwargs
    ):
        if name not in self.action_list:
            raise ValueError(f"不支持的动作: {name}, 可用动作: {list(self.action_list.keys())}")
        act = self.action_list[name]
        method = act.method.copy()
        method["did"] = self.did
        if value is not None:
            method["value"] = value
        if kwargs:
            for k, v in kwargs.items():
                if k.startswith("_"):
                    k = k[1:]
                if k in method:
                    raise ValueError(f"无效的参数: {k}. 请勿使用以下参数 ({', '.join(method.keys())})")
                method[k] = v
        result = self.api.run_action(method)
        if result["code"] == 1:
            logger.warning(f"网关已经接收指令，无法判断是否执行成功: {self.name} -> {name}")
        elif result["code"] != 0:
            raise DeviceActionError(self.name, name, result["code"])
        time.sleep(self.sleep_time)
        logger.debug(f"执行动作: {self.name} -> {name}, 结果: {result}")


def get_device_info(device_model: str, cache_path: Optional[Union[str, Path]] = None) -> dict:
    """
    获取设备规格信息

    根据设备型号获取设备的详细规格信息，包括属性、操作等。
    支持缓存功能，避免重复请求网络。

    参数:
        device_model (str): 设备型号，例如 'yeelink.light.lamp4'
        cache_path (Optional[Union[str, Path]]): 可选，缓存目录路径。
            - 如果为 None，则不使用缓存
            - 如果指定，则将设备信息缓存到该目录下的 {device_model}.json 文件中

    返回值:
        dict: 设备规格信息字典，包含以下字段：
            - name (str): 设备名称
            - model (str): 设备型号
            - properties (list): 设备属性列表，每个属性包含以下字段：
                - name (str): 属性名称
                - description (str): 属性描述
                - type (str): 属性数据类型（int、uint、float、bool、string）
                - rw (str): 读写权限（'r' 可读，'w' 可写，'rw' 可读写）
                - range (list): 属性值范围 [min, max, step]
                - value-list (list): 枚举值列表
                - method (dict): API 调用方法参数
            - actions (list): 设备操作/方法列表，每个操作包含以下字段：
                - name (str): 操作名称
                - description (str): 操作描述
                - method (dict): API 调用方法参数

    异常:
        GetDeviceInfoError: 当获取设备信息失败时抛出

    示例:
        >>> info = get_device_info('yeelink.light.lamp4')
        >>> print(info['name'])  # 输出设备名称
        >>> print(info['properties'][0]['name'])  # 输出第一个属性的名称
    """
    if cache_path is not None:
        cache_file = Path(cache_path) / f"{device_model}.json"
        if cache_file.exists():
            logger.debug(f"从缓存加载设备信息: {cache_file}")
            with cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)
    response = requests.get(device_url + device_model, headers={
        "User-Agent": f"mijiaAPI/{version}"
    })
    if response.status_code != 200:
        raise GetDeviceInfoError(device_model)
    content = re.search(r"<script data-page=\"app\" type=\"application/json\">(.*?)</script>", response.text)
    if content is None:
        raise GetDeviceInfoError(device_model)
    content = content.group(1)
    content = json.loads(content)

    product = content["props"]["product"]
    name = product["name"]
    model = product["model"]
    i18n_zh = content["props"]["i18n"]["zh_cn"]
    result = {
        "name": name,
        "model": model,
        "properties": [],
        "actions": []
    }
    services = content["props"]["tree"]["services"]

    properties_name = []
    actions_name = []
    for svc in services:
        siid = svc["iid"]
        svc_type = svc["type"]
        for prop in svc.get("properties", []):
            piid = prop["iid"]
            if prop["format"].startswith("int"):
                prop_type = "int"
            elif prop["format"].startswith("uint"):
                prop_type = "uint"
            else:
                prop_type = prop["format"]
            access_str = "".join([
                "r" if "read" in prop["access"] else "",
                "w" if "write" in prop["access"] else ""
            ])
            zh_cn = i18n_zh.get(f"service:{siid:03d}:property:{piid:03d}", "")
            item = {
                "name": prop["type"],
                "description": f"{prop['description']} / {zh_cn}".rstrip(" / "),
                "type": prop_type,
                "rw": access_str,
                "range": prop.get("valueRange", None),
                "value-list": None,
                "method": {
                    "siid": siid,
                    "piid": piid
                }
            }
            if prop.get("valueList"):
                item["value-list"] = []
                for vl_item in prop["valueList"]:
                    vl_zh = i18n_zh.get(vl_item.get("i18nKey", ""), "")
                    vl_entry = {
                        "value": vl_item["value"],
                        "description": vl_item["description"]
                    }
                    if vl_zh:
                        vl_entry["desc_zh_cn"] = vl_zh
                    item["value-list"].append(vl_entry)
            if item["name"] in properties_name:
                item["name"] = f"{svc_type}-{item['name']}"
            properties_name.append(item["name"])
            result["properties"].append(item)
        for act in svc.get("actions", []):
            aiid = act["iid"]
            zh_cn = i18n_zh.get(f"service:{siid:03d}:action:{aiid:03d}", "")
            act_item = {
                "name": act["type"],
                "description": f"{act['description']} / {zh_cn}".rstrip(" / "),
                "method": {
                    "siid": siid,
                    "aiid": aiid
                }
            }
            if act_item["name"] in actions_name:
                act_item["name"] = f"{svc_type}-{act_item['name']}"
            actions_name.append(act_item["name"])
            result["actions"].append(act_item)

    if cache_path is not None:
        cache_path = Path(cache_path)
        cache_path.mkdir(parents=True, exist_ok=True)
        cache_file = cache_path / f"{device_model}.json"
        logger.debug(f"缓存设备信息到: {cache_file}")
        with cache_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    return result
