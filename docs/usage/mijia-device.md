# mijiaDevice 高级封装

`mijiaDevice` 类提供了一个高级封装，让您可以像操作普通对象一样控制设备，而无需关心 siid/piid 的细节。

## 初始化设备

```python
from mijiaAPI import mijiaAPI, mijiaDevice

api = mijiaAPI(".mijia-api-data/auth.json")
api.login()

# 通过设备ID初始化
device = mijiaDevice(api, did="device_did")

# 或通过设备名称初始化（推荐，更人性化）
device = mijiaDevice(api, dev_name="我的台灯")

# 打印设备信息
print(device)
```

::: tip
`did` 与 `dev_name` 至少提供一个，同时给出时优先使用 `did`。使用 `dev_name` 时名称必须唯一，否则会抛出 `MultipleDevicesFoundError`。
:::

## 获取和设置属性

```python
# 获取属性值
brightness = device.get('brightness')
print(f"当前亮度: {brightness}%")

# 设置属性值
device.set('brightness', 60)      # 设置亮度为60%
device.set('on', True)            # 打开设备
device.set('color-temperature', 5000)  # 设置色温
```

也可以直接使用属性值赋值的方式，包含 `-` 的属性名请使用下划线 `_` 替代：

```python
print(f"当前亮度: {device.brightness}%")
device.brightness = 60  # 设置亮度为60%
device.on = True        # 打开设备
device.color_temperature = 5000  # 设置色温
```

## 执行设备动作

```python
# 执行动作（如切换开关）
device.run_action('toggle')
```

## 查看设备属性和动作列表

```python
# 查看所有支持的属性
for prop_name, prop_obj in device.prop_list.items():
    print(f"属性: {prop_name} ({prop_obj.desc})")
    print(f"  类型: {prop_obj.type}, 读写: {prop_obj.rw}")

# 查看所有支持的动作
for action_name, action_obj in device.action_list.items():
    print(f"动作: {action_name} ({action_obj.desc})")
```

## sleep_time 参数

在使用 `mijiaDevice` 时，可以设置 `sleep_time` 参数来控制获取属性值时的等待时间。某些设备可能响应较慢，增加此参数可以获取更准确的值：

```python
# 默认 sleep_time 为 0.5 秒
device = mijiaDevice(api, dev_name="我的设备", sleep_time=1.0)

# 获取属性时会自动等待指定的时间
value = device.get('brightness')
```

## 查询设备规格信息

在使用 API 之前，您可以通过以下方式查询设备支持的属性和动作：

```python
from mijiaAPI import get_device_info

# 从米家规格平台获取设备信息
device_info = get_device_info('yeelink.light.lamp4')

# 查看原始信息
import json
print(json.dumps(device_info, ensure_ascii=False, indent=2))

# 或者使用 mijiaDevice 类查看
device = mijiaDevice(api, dev_name="我的台灯")
print(device)  # 会列出所有支持的属性和动作
```

::: tip
完整的方法签名和参数说明请参考 [mijiaDevice 类参考](/reference/mijia-device)。
:::
