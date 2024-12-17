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
device = mijiaDevices(api, dev_info, did=did, sleep_time=2)
print(device)
print('---------------------')
print(device.on)
device.on = True
print('---------------------')
print(f"{device.brightness} {device.prop_list['brightness'].unit}")
device.brightness = 60
print(f"{device.brightness} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
device.color_temperature = 5000
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
print('---------------------')
device.mode = 0
print('---------------------')
print(f"{device.brightness} {device.prop_list['brightness'].unit}")
device.brightness_delta = -10
print(f"{device.brightness} {device.prop_list['brightness'].unit}")
print('---------------------')
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
device.ct_delta = -10
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
device.ct_adjust_alexa_increase = 1
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
device.ct_adjust_alexa_decrease = 2
print(f"{device.color_temperature} {device.prop_list['color-temperature'].unit}")
