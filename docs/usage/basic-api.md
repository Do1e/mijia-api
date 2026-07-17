# API 基础使用

本页介绍 `mijiaAPI` 类的基础 API 调用方式，使用原始的 siid/piid 参数控制设备。

## 获取家庭和设备列表

```python
from mijiaAPI import mijiaAPI

api = mijiaAPI()
api.login()

# 获取所有家庭
homes = api.get_homes_list()
print(homes)

# 获取所有设备（不包含共享设备）
devices = api.get_devices_list()
for device in devices:
    print(f"设备名称: {device['name']}, Model: {device['model']}, Did: {device['did']}")

# 获取指定家庭的设备
home_id = homes[0]['id']
devices_in_home = api.get_devices_list(home_id=home_id)

# 获取共享设备列表（无法指定家庭ID）
shared_devices = api.get_shared_devices_list()
```

## 获取和设置设备属性

```python
# 获取设备属性（原始 siid/piid 方式）
result = api.get_devices_prop({
    "did": "device_did",
    "siid": 2,
    "piid": 2
})
print(f"属性值: {result['value']}")

# 设置设备属性
result = api.set_devices_prop({
    "did": "device_did",
    "siid": 2,
    "piid": 2,
    "value": 50
})

# 支持批量操作
result = api.get_devices_prop([
    {"did": "device_did1", "siid": 2, "piid": 2},
    {"did": "device_did2", "siid": 2, "piid": 2},
])
```

## 执行设备动作

```python
# 执行设备动作（如开关灯的切换动作）
result = api.run_action({
    "did": "device_did",
    "siid": 2,
    "aiid": 1
})
```

## 场景控制

```python
# 获取场景列表
scenes = api.get_scenes_list()

# 执行场景
result = api.run_scene(scene_id="scene_id", home_id="home_id")
```

## 耗材管理

```python
# 获取耗材列表（如滤芯、灯泡等）
consumables = api.get_consumable_items()

# 获取指定家庭的耗材
consumables_in_home = api.get_consumable_items(home_id=home_id)
```

## 统计数据

```python
import json
import time

# 获取 lumi.acpartner.mcn04 过去约 6 个月的月度耗电量
result = api.get_statistics({
    "did": "device_did",
    "key": "7.1",
    "data_type": "stat_month_v3",
    "limit": 6,                      # 返回的最大条目数
    "time_start": int(time.time() - 30 * 24 * 3600 * 6),
    "time_end": int(time.time()),
})

for item in result:
    value = json.loads(item["value"])[0]
    print(f"时间: {item['time']}, 数值: {value}")
```

常用统计类型为 `stat_hour_v3`、`stat_day_v3`、`stat_week_v3`、`stat_month_v3`；
较旧设备可能使用不带 `_v3` 的对应类型。`key` 同样依赖设备型号，例如
`lumi.acpartner.mcn04` 的耗电量使用 `"7.1"`，`lumi.acpartner.mcn02` 使用 `"powerCost"`。

::: warning
统计接口仅支持部分设备，不同型号可能使用不同 API。详见
[issue #46](https://github.com/Do1e/mijia-api/issues/46) 和
[米家统计接口文档](https://iot.mi.com/new/doc/accesses/direct-access/extension-development/extension-functions/statistical-interface)。
:::

## 设备信息获取

使用 `get_device_info()` 函数可从[米家规格平台](https://home.miot-spec.com/)在线获取设备属性和动作信息：

```python
from mijiaAPI import get_device_info

# 获取设备规格信息
device_info = get_device_info('yeelink.light.lamp4')  # 米家台灯 1S 的 model

# 查看设备支持的属性和动作
print(device_info)
```

::: tip
完整的 API 方法签名和参数说明请参考 [API 参考](/reference/mijia-api)。
:::
