from typing import Union, Optional
import json
import re
import requests
from time import sleep
from .apis import mijiaAPI
from .urls import deviceURL

class DevProp(object):
    def __init__(self, prop_dict: dict):
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
        return f'  {self.name}: {self.desc}\n' \
               f'    valuetype: {self.type}, rw: {self.rw}, unit: {self.unit}, range: {self.range}' + \
               (('\n    ' + ', '.join([f'{item["value"]}: {item["description"]}' for item in self.value_list])) if self.value_list else '')

class DevAction(object):
    def __init__(self, act_dict: dict):
        self.name = act_dict['name']
        self.desc = act_dict['description']
        self.method = act_dict['method']

    def __str__(self):
        return f'  {self.name}: {self.desc}'

class mijiaDevices(object):
    def __init__(self, api: mijiaAPI, dev_info: dict,
                 did: Optional[str] = None,
                 sleep_time: Optional[Union[int, float]] = 0.5):
        self.api = api
        self.name = dev_info['name']
        self.model = dev_info['model']
        self.prop_list = {prop['name']: DevProp(prop) for prop in dev_info['properties']}
        self.prop_list.update({prop['name'].replace('-', '_'): DevProp(prop) for prop in dev_info['properties'] if '-' in prop['name']})
        if 'actions' in dev_info:
            self.action_list = {act['name']: DevAction(act) for act in dev_info['actions']}
        else:
            self.action_list = {}
        self.did = did
        self.sleep_time = sleep_time

    def __str__(self):
        prop_list = [str(v) for k, v in self.prop_list.items() if '_' not in k]
        action_list = [str(v) for v in self.action_list.values()]
        return f'{self.name} ({self.model})\n' \
               'Properties:\n' + '\n'.join(prop_list) + '\n' \
               'Actions:\n' + '\n'.join(action_list)

    def set(self, name: str, did: str, value: Union[bool, int]) -> Union[bool, int]:
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
                        raise ValueError(f'Invalid value: {value}, should be in range {prop.range[:2]} with step {prop.range[2]}')
        elif prop.type == 'float':
            value = float(value)
            if prop.range:
                if value < prop.range[0] or value > prop.range[1]:
                    raise ValueError(f'Value out of range: {value}, should be in range {prop.range[:2]}')
                if len(prop.range) >= 3 and isinstance(prop.range[2], int):
                    if int(value - prop.range[0]) % prop.range[2] != 0:
                        raise ValueError(f'Invalid value: {value}, should be in range {prop.range[:2]} with step {prop.range[2]}')
        elif prop.type == 'string':
            if not isinstance(value, str):
                raise ValueError(f'Invalid value for string: {value}, should be a string')
        else:
            raise ValueError(f'Unsupported type: {prop.type}, available types: bool, int, uint, float, string')
        method = prop.method.copy()
        method['did'] = did
        method['value'] = value
        ret = self.api.set_devices_prop([method])[0]['code'] == 0
        sleep(self.sleep_time)
        return ret

    def set_v2(self, name: str, value: Union[bool, int], did: Optional[str] = None) -> Union[bool, int]:
        if did is not None:
            return self.set(name, did, value)
        elif self.did is not None:
            return self.set(name, self.did, value)
        else:
            raise ValueError('Please specify the did')

    def get(self, name: str, did: Optional[str] = None) -> Union[bool, int]:
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
        ret = self.api.get_devices_prop([method])[0]['value']
        sleep(self.sleep_time)
        return ret

    def __setattr__(self, name: str, value: Union[bool, int]) -> None:
        if 'prop_list' in self.__dict__ and name in self.prop_list:
            if not self.set_v2(name, value):
                raise RuntimeError(f'Failed to set property: {name}')
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Union[bool, int]:
        if 'prop_list' in self.__dict__ and name in self.prop_list:
            return self.get(name)
        else:
            return super().__getattr__(name)

    def run_action(self, name: str, did: Optional[str] = None, value: Optional[Union[list, tuple]] = None, **kwargs) -> bool:
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
                    raise ValueError(f'Invalid argument: {k}, available arguments: {list(method.keys())}')
                method[k] = v
        ret = self.api.run_action(method)['code'] == 0
        sleep(self.sleep_time)
        return ret

def get_device_info(device_model: str) -> dict:
    response = requests.get(deviceURL + device_model)
    if response.status_code != 200:
        raise RuntimeError(f'Failed to get device info')
    content = re.search(r'data-page="(.*?)">', response.text)
    if content is None:
        raise RuntimeError(f'Failed to get device info')
    content = content.group(1)
    content = json.loads(content.replace('&quot;', '"'))

    result = {}
    result['name'] = content['props']['product']['name']
    result['model'] = content['props']['product']['model']
    result['properties'] = []
    result['actions'] = []
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
                item ={
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
                if item['range'] is not None:
                    item['range'] = item['range']
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
