import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaDevice, mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)

with open('demos/dev_info_example/miaomiaoce.sensor_ht.t1.json', encoding='utf-8') as f:
    dev_info = json.load(f)
with open('jsons/devices.json') as f:
    devices = json.load(f)
    did = devices[5]['did']
device = mijiaDevice(api, dev_info)
print(device)
print('---------------------')
print(device.get('temperature', did))
print(device.get('relative-humidity', did))
print(device.get('battery-level', did))
