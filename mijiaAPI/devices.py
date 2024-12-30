from typing import Union, Optional
from time import sleep
from .apis import mijiaAPI

import json
import requests
from lxml import etree
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
        self.method = prop_dict['method']

    def __str__(self):
        return f'  {self.name}: {self.desc}\n' \
               f'    valuetype: {self.type}, rw: {self.rw}, unit: {self.unit}, range: {self.range}'

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
        if prop.type == 'bool':
            if not isinstance(value, bool):
                raise ValueError(f'Invalid value for bool: {value}, should be True or False')
        elif prop.type in ['int', 'uint']:
            try:
                value = int(value)
                if prop.range:
                    if value < prop.range[0] or value > prop.range[1]:
                        raise ValueError(f'Value out of range: {value}, should be in range {prop.range}')
            except ValueError:
                raise ValueError(f'Invalid value for int: {value}, should be an integer')
        elif prop.type == 'float':
            try:
                value = float(value)
                if prop.range:
                    if value < prop.range[0] or value > prop.range[1]:
                        raise ValueError(f'Value out of range: {value}, should be in range {prop.range}')
            except ValueError:
                raise ValueError(f'Invalid value for float: {value}, should be a float')
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

    def run_action(self, name: str, did: Optional[str] = None, value: Optional[Union[list, tuple]] = None) -> bool:
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
        ret = self.api.run_action(method)['code'] == 0
        sleep(self.sleep_time)
        return ret
    
def get_device_info(device_model: str) -> dict:
    response = response = requests.get(f'{deviceURL}{device_model}')
    html = etree.HTML(response.text)
    content = json.loads(str(html.xpath('//div[@id="app"]/@data-page')[0]))

    result = {}
    result['name'] = content['props']['product']['name']
    result['model'] = content['props']['product']['model']
    properties = []
    actions = []

    for siid in content['props']['spec']['services'].keys():
        if 'properties' in content['props']['spec']['services'][siid].keys():
            for piid in content['props']['spec']['services'][siid]['properties'].keys():
                properties.append({
                    'name': content['props']['spec']['services'][siid]['properties'][piid]['name'],
                    'description': content['props']['spec']['services'][siid]['properties'][piid]['description'],
                    # https://iot.mi.com/v2/new/doc/introduction/knowledge/spec
                    'type': {
                        'bool': 'bool',
                        'uint8': 'int',
                        'uint16': 'int',
                        'uint32': 'int',
                        'int8': 'int',
                        'int16': 'int',
                        'int32': 'int',
                        'int64': 'int',
                        'float': 'float',
                        'string': 'string',
                        'hex': 'hex'
                    }[content['props']['spec']['services'][siid]['properties'][piid]['format']],
                    'rw': ''.join([
                        'r' if 'read'  in content['props']['spec']['services'][siid]['properties'][piid]['access'] else '',
                        'w' if 'write' in content['props']['spec']['services'][siid]['properties'][piid]['access'] else '',
                    ]),
                    'unit': content['props']['spec']['services'][siid]['properties'][piid].get('unit', None),
                    'range': content['props']['spec']['services'][siid]['properties'][piid]['value-range'][:2] if 'value-range' in content['props']['spec']['services'][siid]['properties'][piid].keys() else None,
                    'method': {
                        'siid': siid,
                        'piid': piid
                    }
                })
        if 'actions' in content['props']['spec']['services'][siid].keys():
            for aiid in content['props']['spec']['services'][siid]['actions'].keys():
                actions.append({
                    'name': content['props']['spec']['services'][siid]['actions'][aiid]['name'],
                    'description': content['props']['spec']['services'][siid]['actions'][aiid]['description'],
                    'method': {
                        'siid': int(siid),
                        'aiid': int(aiid)
                    },
                    'in': [ { 'siid': siid, 'piid': in_piid } for in_piid in content['props']['spec']['services'][siid]['actions'][aiid]['in']]
                })
        
    result['properties'] = properties
    result['actions'] = actions

    return result
