import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaDevice, mijiaAPI

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
device = mijiaDevice(api, dev_info, sleep_time=2)
print(device)
print('---------------------')
print(device.get('on', did))
print(device.set('on', True, did))
print('---------------------')
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print(device.set('brightness', 60, did))
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('color-temperature', 5000, did))
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print('---------------------')
print(device.set('mode', 0, did))
print('---------------------')
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print(device.set('brightness-delta', -10, did))
print(f"{device.get('brightness', did)} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-delta', -10, did))
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-adjust-alexa', 1, did)) # increase
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print(device.set('ct-adjust-alexa', 2, did)) # decrease
print(f"{device.get('color-temperature', did)} {device.prop_list['color-temperature'].unit}")
print('---------------------')
print(device.run_action('toggle', did))
