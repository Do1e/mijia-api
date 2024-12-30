import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaDevices, mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)

with open('jsons/devices.json') as f:
    devices = json.load(f)
    did = devices[2]['did']
dev_info = {
    "name": "米家空调伴侣Pro 万能遥控版",
    "model": "lumi.acpartner.mcn04",
    "properties": [
        {
            "name": "on",
            "description": "开关",
            "type": "bool",
            "rw": "rw",
            "unit": None,
            "range": None,
            "method": {
                "siid": 3,
                "piid": 1
            }
        },
        {
            "name": "mode",
            "description": "空调模式，0-4分别是制冷、制热、自动、送风、除湿",
            "type": "uint",
            "rw": "rw",
            "unit": None,
            "range": [0, 4],
            "method": {
                "siid": 3,
                "piid": 2
            }
        },
        {
            "name": "target-temperature",
            "description": "目标温度",
            "type": "uint",
            "rw": "rw",
            "unit": "celsius",
            "range": [16, 30],
            "method": {
                "siid": 3,
                "piid": 4
            }
        },
        {
            "name": "power-consumption",
            "description": "耗电量",
            "type": "float",
            "rw": "r",
            "unit": None,
            "range": [0, 3.4e38],
            "method": {
                "siid": 7,
                "piid": 1
            }
        },
        {
            "name": "electric-power",
            "description": "功率",
            "type": "float",
            "rw": "r",
            "unit": "watt",
            "range": [0, 3.4e38],
            "method": {
                "siid": 7,
                "piid": 2
            }
        },
    ],
    "actions": [
        {
            "name": "toggle",
            "description": "开关",
            "method": {
                "siid": 3,
                "aiid": 1
            }
        }
    ]
}

# sleep_time is optional, default is 0.5
# get after set shuold be delayed for a while, or the result may be incorrect
device = mijiaDevices(api, dev_info, sleep_time=2)
print(device)
print('---------------------')
print(device.get('on', did))
print(device.set('on', did, True))
print(device.get('on', did))
print('---------------------')
print(device.get('mode', did))
print('---------------------')
print(device.get('target-temperature', did))
print(device.set('target-temperature', did, 26))
print(device.get('target-temperature', did))
print('---------------------')
print(device.get('power-consumption', did))
print(device.get('electric-power', did))
print('---------------------')
print(device.run_action('toggle', did))
