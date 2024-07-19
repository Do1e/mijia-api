from typing import Union
from time import sleep
from .apis import mijiaAPI

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
        return f'{self.name}: {self.desc}\n' \
               f'  valuetype: {self.type}, rw: {self.rw}, unit: {self.unit}, range: {self.range}'

class mijiaDevices(object):
    def __init__(self, api: mijiaAPI, dev_info: dict, sleep_time: float = 0.5):
        self.api = api
        self.name = dev_info['name']
        self.model = dev_info['model']
        self.prop_list = {prop['name']: DevProp(prop) for prop in dev_info['properties']}
        self.sleep_time = sleep_time

    def __str__(self):
        return f'{self.name} ({self.model})\n' \
               f'Properties:\n' + '\n'.join([str(v) for v in self.prop_list.values()])

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

    def get(self, name: str, did: str) -> Union[bool, int]:
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
