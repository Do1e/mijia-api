import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaDevices, mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)

with open('demos/dev_info_example/yeelink.light.lamp4.json', encoding='utf-8') as f:
    dev_info = json.load(f)
with open('jsons/devices.json') as f:
    devices = json.load(f)
    did = devices[0]['did']
# sleep_time is optional, default is 0.5
# get after set shuold be delayed for a while, or the result may be incorrect
device = mijiaDevices(api, dev_info, sleep_time=2)
print(device)
print('---------------------')
print(device.get('on', did))
print(device.set('on', did, True))
print('---------------------')
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print(device.set('brightness', did, 60))
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('color-temperature', did, 5000))
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print('---------------------')
print(device.set('mode', did, 0))
print('---------------------')
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print(device.set('brightness-delta', did, -10))
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-delta', did, -10))
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-adjust-alexa', did, 1)) # increase
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-adjust-alexa', did, 2)) # decrease
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print('---------------------')
print(device.run_action('toggle', did))
