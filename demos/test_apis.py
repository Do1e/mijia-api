import json
import logging
import time

from mijiaAPI import mijiaAPI


logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

api = mijiaAPI(".mijia-api-data/auth.json")

# ----------------------- get homes list -----------------------
homes = api.get_homes_list()
with open(".mijia-api-data/homes.json", "w", encoding="utf-8") as f:
    json.dump(homes, f, ensure_ascii=False, indent=2)
time.sleep(1)
home_id = homes[0]['id']
home_name = homes[0]['name']

# ---------------------- get devices list ----------------------
devices = api.get_devices_list()
with open(".mijia-api-data/devices.json", "w", encoding="utf-8") as f:
    json.dump(devices, f, ensure_ascii=False, indent=2)
time.sleep(1)

# -------------------- get shared homes list -------------------
shared_devices = api.get_shared_devices_list()
with open(".mijia-api-data/shared_devices.json", "w", encoding="utf-8") as f:
    json.dump(shared_devices, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ------------------ get devices with home_id ------------------
devices_with_home = api.get_devices_list(home_id=home_id)
with open(f".mijia-api-data/devices_in_{home_name}.json", "w", encoding="utf-8") as f:
    json.dump(devices_with_home, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ---------------------- get scenes list -----------------------
scenes = api.get_scenes_list()
with open(".mijia-api-data/scenes.json", "w", encoding="utf-8") as f:
    json.dump(scenes, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ------------------ get scenes with home_id -------------------
scenes_with_home = api.get_scenes_list(home_id=home_id)
with open(f".mijia-api-data/scenes_in_{home_name}.json", "w", encoding="utf-8") as f:
    json.dump(scenes_with_home, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ------------------------- run scene --------------------------
scence_id = scenes[0]['scene_id']
scence_name = scenes[0]['name']
scence_home_id = scenes[0]['home_id']
ret = api.run_scene(scence_id, scence_home_id)
print(f"已执行场景 {scence_name}，响应: {ret}")
time.sleep(1)

# -------------------- get consumable items --------------------
consumable_items = api.get_consumable_items()
with open(".mijia-api-data/consumable_items.json", "w", encoding="utf-8") as f:
    json.dump(consumable_items, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ------------- get consumable items with home_id --------------
consumable_items_with_home = api.get_consumable_items(home_id=home_id)
with open(f".mijia-api-data/consumable_items_in_{home_name}.json", "w", encoding="utf-8") as f:
    json.dump(consumable_items_with_home, f, ensure_ascii=False, indent=2)
time.sleep(1)

# ----------------- get/set device properties ------------------
# did 和 model 从 get_devices_list() 接口获取
# siid 和 piid 请查阅 https://home.miot-spec.com/spec/{model}
# 或者也可以直接在 米家APP->智能->+->手动控制 中
# 添加 scene，调用 run_scene() 接口控制设备
for device in devices:
    if device["model"] == "yeelink.light.lamp4":
        break

did = device["did"]
name = device["name"]

ret = api.get_devices_prop([
    {"did": did, "siid": 2, "piid": 2},
    {"did": did, "siid": 2, "piid": 3},
])
brightness = ret[0]["value"]
color_temperature = ret[1]["value"]
print(f"获取设备 {name} 属性成功: {ret}")
print(f"亮度: {brightness}%")
print(f"色温: {color_temperature}K")

ret = api.set_devices_prop([
    {"did": did, "siid": 2, "piid": 2, "value": 50},
    {"did": did, "siid": 2, "piid": 3, "value": 2700},
])
print(f"设置设备 {name} 属性成功: {ret}")
time.sleep(1)

# ------------------------- run action -------------------------
ret = api.run_action({"did": did, "siid": 2, "aiid": 1})
print(f"执行设备 {name} 动作成功: {ret}")
time.sleep(1)

# ----------------------- get statistics -----------------------
for device in devices:
    if device["model"] == "lumi.acpartner.mcn04":
        break
ret = api.get_statistics({
    "did": device["did"],
    "key": "7.1",
    "data_type": "stat_month_v3",
    "limit": 6,
    "time_start": int(time.time() - 24 * 60 * 60 * 30 * 6),
    "time_end": int(time.time()),
})
print(f"获取设备 {device['name']} 统计数据成功: {ret}")
