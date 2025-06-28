import json
import time
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)


# ---------------------- get devices list ----------------------
devices = api.get_devices_list()
with open('jsons/devices.json', 'w') as f:
    json.dump(devices, f, indent=2, ensure_ascii=False)
time.sleep(2)

# ---------------------- get homes list ------------------------
homes = api.get_homes_list()
with open('jsons/homes.json', 'w') as f:
    json.dump(homes, f, indent=2, ensure_ascii=False)
time.sleep(2)

# ---------------------- get scenes list -----------------------
home_id = homes[0]['id']
home_owner_id = homes[0]['uid']
scenes = api.get_scenes_list(home_id)
with open('jsons/scenes.json', 'w') as f:
    json.dump(scenes, f, indent=2, ensure_ascii=False)
time.sleep(2)

# ---------------------- run scene -----------------------------
scence_id = scenes[0]['scene_id']
scence_name = scenes[0]['name']
ret = api.run_scene(scence_id)
print(f'运行场景 {scence_name}: {ret}')
time.sleep(2)

# ---------------------- get consumable items ------------------
consumable_items = api.get_consumable_items(home_id, owner_id=home_owner_id)
with open('jsons/consumable_items.json', 'w') as f:
    json.dump(consumable_items, f, indent=2, ensure_ascii=False)
time.sleep(2)

# ---------------------- get/set device properties -------------
# look for did and model in devices.json
# look for siid and piid in https://home.miot-spec.com/spec/{model}
# or it's feasible to use `run_scene`` to set the device properties
did = devices[0]['did']
name = devices[0]['name']
ret = api.get_devices_prop([
    {"did": did, "siid": 2, "piid": 2},
    {"did": did, "siid": 2, "piid": 3},
])
brightness = ret[0]['value']
color_temperature = ret[1]['value']
print(f'获取设备 {name} 属性:\n亮度: {brightness}%\n'
      f'色温: {color_temperature}K')
time.sleep(2)

ret = api.set_devices_prop([
    {"did": did, "siid": 2, "piid": 2, "value": 50},
    {"did": did, "siid": 2, "piid": 3, "value": 2700},
])
print(f'设置设备 {name} 属性:\n'
      f'亮度: {"成功" if ret[0]["code"] == 0 else "失败"}\n'
      f'色温: {"成功" if ret[1]["code"] == 0 else "失败"}')

# ---------------------- run action ----------------------------
did = devices[0]['did']
ret = api.run_action({"did": did, "siid": 2, "aiid": 1})
print(f'开关切换: {"成功" if ret["code"] == 0 else "失败"}')
