from typing import Union, Optional
import json
import re
import requests
from time import sleep
from .apis import mijiaAPI
from .code import ERROR_CODE
from .urls import deviceURL
from .logger import logger

class DevProp(object):
    def __init__(self, prop_dict: dict):
        """
        Initialize the property object 初始化属性对象
        :param prop_dict:
        """
        self.name = prop_dict['name']
        self.desc = prop_dict['description']
        self.type = prop_dict['type']
        if self.type not in ['bool', 'int', 'uint', 'float', 'string']:
            raise ValueError(f'Unsupported type: {self.type}, available types: bool, int, uint, float, string')
        self.rw = prop_dict['rw']
        self.unit = prop_dict['unit']
        self.range = prop_dict['range']
        self.value_list = prop_dict.get('value-list', None)
        self.method = prop_dict['method']

    def __str__(self):
        """
        String representation of the property 返回属性的名称、描述、类型、读写权限、单位和范围
        :return:
        """
        lines = [
            f"  {self.name}: {self.desc}",
            f"    valuetype: {self.type}, rw: {self.rw}, unit: {self.unit}, range: {self.range}"
        ]

        if self.value_list:
            value_lines = [f"    {item['value']}: {item['description']}" for item in self.value_list]
            lines.extend(value_lines)

        return '\n'.join(lines)


class DevAction(object):
    def __init__(self, act_dict: dict):
        self.name = act_dict['name']
        self.desc = act_dict['description']
        self.method = act_dict['method']

    def __str__(self):
        return f'  {self.name}: {self.desc}'


class mijiaDevices(object):
    def __init__(
            self,
            api: mijiaAPI,
            dev_info: Optional[dict] = None,
            dev_name: Optional[str] = None,
            did: Optional[str] = None,
            sleep_time: Optional[Union[int, float]] = 0.5
    ):
        """
        Initialize the device object 初始化设备对象
        若未提供设备信息，则根据设备名称获取设备信息，若两者均未提供，则抛出异常
        若提供了设备信息的同时提供了设备名称，则以设备信息为准
        :param api: 米家API对象
        :param dev_info: 设备信息字典（可选）
        :param dev_name: 设备名称（可选）
        :param did: 设备ID（可选）
        :param sleep_time: 调用设备属性的间隔时间（可选，默认0.5秒）
        """
        assert dev_info is not None or dev_name is not None, "Either 'dev_info' or 'dev_name' must be provided."
        if dev_info is not None and dev_name is not None:
            logger.warning("Both 'dev_info' and 'dev_name' provided. Using 'dev_info' for initialization.")

        self.api = api
        if dev_info is None:
            devices_list = self.api.get_devices_list()
            matches = [device for device in devices_list.get('list', []) if device['name'] == dev_name]
            if not matches:
                raise ValueError(f"Device {dev_name} not found")
            elif len(matches) > 1:
                raise ValueError(f"Multiple devices named {dev_name} found")
            else:
                dev_info = get_device_info(matches[0]['model'])
                did = matches[0]['did']
        self.name = dev_info['name']
        self.model = dev_info['model']

        self.prop_list = {}
        for prop in dev_info.get('properties', []):
            prop_obj = DevProp(prop)
            name = prop['name']
            self.prop_list[name] = prop_obj
            if '-' in name:
                self.prop_list[name.replace('-', '_')] = prop_obj

        self.action_list = {
            act['name']: DevAction(act)
            for act in dev_info.get('actions', [])
        }
        self.did = did
        self.sleep_time = sleep_time

    def __str__(self) -> str:
        """
        String representation of the device 返回设备的属性和动作列表
        :return: 设备的属性和动作列表
        """
        prop_list_str = '\n'.join(filter(None, (str(v) for k, v in self.prop_list.items() if '_' not in k)))
        action_list_str = '\n'.join(map(str, self.action_list.values()))
        return (f"{self.name} ({self.model})\n"
                f"Properties:\n{prop_list_str if prop_list_str else 'No properties available'}\n"
                f"Actions:\n{action_list_str if action_list_str else 'No actions available'}")

    def set(self, name: str, did: str, value: Union[bool, int]) -> Union[bool, int]:
        """
        Set property value 设置设备的属性值
        :param name: 属性名称
        :param did: 设备ID
        :param value: 属性值
        :return: 执行结果（True/False）
        """
        if name not in self.prop_list:
            raise ValueError(f'Unsupported property: {name}, available properties: {list(self.prop_list.keys())}')
        prop = self.prop_list[name]
        if 'w' not in prop.rw:
            raise ValueError(f'Property {name} is read-only')
        if prop.value_list:
            if value not in [item['value'] for item in prop.value_list]:
                raise ValueError(f'Invalid value: {value}, should be in {prop.value_list}')
        if prop.type == 'bool':
            if not isinstance(value, bool):
                raise ValueError(f'Invalid value for bool: {value}, should be True or False')
        elif prop.type in ['int', 'uint']:
            value = int(value)
            if prop.range:
                if value < prop.range[0] or value > prop.range[1]:
                    raise ValueError(f'Value out of range: {value}, should be in range {prop.range[:2]}')
                if len(prop.range) >= 3 and prop.range[2] != 1:
                    if (value - prop.range[0]) % prop.range[2] != 0:
                        raise ValueError(
                            f'Invalid value: {value}, should be in range {prop.range[:2]} with step {prop.range[2]}')
        elif prop.type == 'float':
            value = float(value)
            if prop.range:
                if value < prop.range[0] or value > prop.range[1]:
                    raise ValueError(f'Value out of range: {value}, should be in range {prop.range[:2]}')
                if len(prop.range) >= 3 and isinstance(prop.range[2], int):
                    if int(value - prop.range[0]) % prop.range[2] != 0:
                        raise ValueError(
                            f'Invalid value: {value}, should be in range {prop.range[:2]} with step {prop.range[2]}')
        elif prop.type == 'string':
            if not isinstance(value, str):
                raise ValueError(f'Invalid value for string: {value}, should be a string')
        else:
            raise ValueError(f'Unsupported type: {prop.type}, available types: bool, int, uint, float, string')
        method = prop.method.copy()
        method['did'] = did
        method['value'] = value
        result = self.api.set_devices_prop([method])[0]
        if result['code'] != 0:
            raise RuntimeError(
                f"Failed to set property: {name}, "
                f"code: {result['code']}, "
                f"message: {ERROR_CODE.get(str(result['code']), 'Unknown error')}"
            )
        sleep(self.sleep_time)
        return result['code'] == 0

    def set_v2(self, name: str, value: Union[bool, int], did: Optional[str] = None) -> Union[bool, int]:
        """
        Set property value_v2 设置设备的属性值_v2（需在实例化时指定did）
        :param name: 属性名称
        :param value: 属性值
        :param did: 设备ID（若未指定，则使用实例化时的did）
        :return: 执行结果（True/False）
        """
        if did is not None:
            return self.set(name, did, value)
        elif self.did is not None:
            return self.set(name, self.did, value)
        else:
            raise ValueError('Please specify the did')

    def get(self, name: str, did: Optional[str] = None) -> Union[bool, int]:
        """
        Get property value 获取设备的属性值
        :param name: 属性名称
        :param did: 设备ID（若未指定，则使用实例化时的did）
        :return: 属性值
        """
        if did is None:
            did = self.did
        if did is None:
            raise ValueError('Please specify the did')
        if name not in self.prop_list:
            raise ValueError(f'Unsupported property: {name}, available properties: {list(self.prop_list.keys())}')
        prop = self.prop_list[name]
        if 'r' not in prop.rw:
            raise ValueError(f'Property {name} is write-only')
        method = prop.method.copy()
        method['did'] = did
        result = self.api.get_devices_prop([method])[0]
        if result['code'] != 0:
            raise RuntimeError(
                f"Failed to get property: {name}, "
                f"code: {result['code']}, "
                f"message: {ERROR_CODE.get(str(result['code']), 'Unknown error')}"
            )
        sleep(self.sleep_time)
        return result['value']

    def __setattr__(self, name: str, value: Union[bool, int]) -> None:
        """
        Set property value 设置设备的属性值（需在实例化时指定did）
        :param name: 属性名称
        :param value: 属性值
        :return: None
        """
        if 'prop_list' in self.__dict__ and name in self.prop_list:
            if not self.set_v2(name, value):
                raise RuntimeError(f'Failed to set property: {name}')
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Union[bool, int]:
        """
        Get property value 获取设备的属性值（需在实例化时指定did）
        :param name: 属性名称
        :return: 属性值
        """
        if 'prop_list' in self.__dict__ and name in self.prop_list:
            return self.get(name)
        else:
            return super().__getattr__(name)

    def run_action(
            self,
            name: str,
            did: Optional[str] = None,
            value: Optional[Union[list, tuple]] = None,
            **kwargs
    ) -> bool:
        """
        Run action 运行设备动作
        :param name: 动作名称
        :param did: 设备ID（若未指定，则使用实例化时的did）
        :param value: 动作参数（若动作不需要参数，则不需要指定）
        :param kwargs: 其它动作参数（若动作不需要参数，则不需要指定）
        :return: 执行结果（True/False）
        """
        if did is None:
            did = self.did
        if did is None:
            raise ValueError('Please specify the did')
        if name not in self.action_list:
            raise ValueError(f'Unsupported action: {name}, available actions: {list(self.action_list.keys())}')
        act = self.action_list[name]
        method = act.method.copy()
        method['did'] = did
        if value is not None:
            method['value'] = value
        if kwargs:
            for k, v in kwargs.items():
                if k.startswith("_"):
                    k = k[1:]
                if k in method:
                    raise ValueError(f'Invalid argument: {k}. Do not use arguments in ({", ".join(method.keys())})')
                method[k] = v
        result = self.api.run_action(method)
        if result['code'] != 0:
            raise RuntimeError(
                f"Failed to run action: {name}, "
                f"code: {result['code']}, "
                f"message: {ERROR_CODE.get(str(result['code']), 'Unknown error')}"
            )
        sleep(self.sleep_time)
        return result['code'] == 0


def get_device_info(device_model: str) -> dict:
    """
    Get device info 获取设备信息
    :param device_model: 设备型号
    :return: 设备信息字典
    """
    response = requests.get(deviceURL + device_model)
    if response.status_code != 200:
        raise RuntimeError(f'Failed to get device info')
    content = re.search(r'data-page="(.*?)">', response.text)
    if content is None:
        raise RuntimeError(f'Failed to get device info')
    content = content.group(1)
    content = json.loads(content.replace('&quot;', '"'))

    result = {
        'name': content['props']['product']['name'],
        'model': content['props']['product']['model'],
        'properties': [],
        'actions': []
    }
    services = content['props']['spec']['services']

    properties_name = []
    actions_name = []
    for siid in services:
        if 'properties' in services[siid]:
            for piid in services[siid]['properties']:
                prop = services[siid]['properties'][piid]
                if prop['format'].startswith('int'):
                    prop_type = 'int'
                elif prop['format'].startswith('uint'):
                    prop_type = 'uint'
                else:
                    prop_type = prop['format']
                item = {
                    'name': prop['name'],
                    'description': prop['description'],
                    'type': prop_type,
                    'rw': ''.join([
                        'r' if 'read' in prop['access'] else '',
                        'w' if 'write' in prop['access'] else ''
                    ]),
                    'unit': prop.get('unit', None),
                    'range': prop.get('value-range', None),
                    'value-list': prop.get('value-list', None),
                    'method': {
                        'siid': int(siid),
                        'piid': int(piid)
                    }
                }
                if item['name'] in properties_name:
                    item["name"] = f'{services[siid]["name"]}-{item["name"]}'
                properties_name.append(item['name'])
                result['properties'].append({k: None if v == 'none' else v for k, v in item.items()})
        if 'actions' in services[siid]:
            for aiid in services[siid]['actions']:
                act = services[siid]['actions'][aiid]
                if act['name'] in actions_name:
                    act['name'] = f'{services[siid]["name"]}-{act["name"]}'
                actions_name.append(act['name'])
                result['actions'].append({
                    'name': act['name'],
                    'description': act['description'],
                    'method': {
                        'siid': int(siid),
                        'aiid': int(aiid)
                    }
                })
    return result
