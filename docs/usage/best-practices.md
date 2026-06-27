# 最佳实践

## 设置 sleep_time 参数

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

## 使用正确的认证文件路径

认证文件默认保存在用户主目录 `~/.config/mijia-api/auth.json`，您也可以自定义路径：

```python
from pathlib import Path

# 默认方式（推荐，认证文件保存在 ~/.config/mijia-api/auth.json）
api = mijiaAPI()

# 方案1：保存在项目目录
auth_path = Path(__file__).parent / ".mijia-api" / "auth.json"
api = mijiaAPI(str(auth_path))

# 方案2：直接传入目录，自动创建 auth.json
api = mijiaAPI(".mijia-api-data")
```

## 批量操作性能优化

对多个设备进行操作时，建议使用批量操作而不是逐个操作：

```python
# 低效方式：逐个获取
for device_id in device_ids:
    result = api.get_devices_prop({"did": device_id, "siid": 2, "piid": 2})

# 高效方式：批量获取
props_list = [{"did": device_id, "siid": 2, "piid": 2} for device_id in device_ids]
results = api.get_devices_prop(props_list)
```

## 查看 debug 日志

如果遇到问题，可以启用 debug 日志来了解详细的 API 调用过程：

```python
import logging

# 启用 debug 日志
logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

# 现在所有 API 调用都会打印详细的日志
api = mijiaAPI()
api.login()
```

## 异常处理

在使用过程中可能遇到各种异常，以下是常见的异常类型及处理方式：

```python
from mijiaAPI import (
    mijiaAPI,
    mijiaDevice,
    LoginError,
    DeviceNotFoundError,
    DeviceGetError,
    DeviceSetError,
    DeviceActionError,
    APIError,
)

api = mijiaAPI()

try:
    # 登录异常
    api.login()
except LoginError as e:
    print(f"登录失败: {e}")
    exit(1)

try:
    # 设备不存在异常
    device = mijiaDevice(api, dev_name="不存在的设备")
except DeviceNotFoundError as e:
    print(f"设备未找到: {e}")
except MultipleDevicesFoundError as e:
    print(f"找到多个匹配的设备: {e}")
except Exception as e:
    print(f"其他异常: {e}")

try:
    # 获取属性异常
    device = mijiaDevice(api, dev_name="我的台灯")
    brightness = device.get('brightness')
except DeviceGetError as e:
    print(f"获取属性失败: {e}")
except ValueError as e:
    print(f"属性名称不支持: {e}")

try:
    # 设置属性异常
    device.set('brightness', 150)  # 超出范围
except DeviceSetError as e:
    print(f"设置属性失败: {e}")
except ValueError as e:
    print(f"属性值无效: {e}")

try:
    # 执行动作异常
    device.run_action('invalid_action')
except DeviceActionError as e:
    print(f"执行动作失败: {e}")
except ValueError as e:
    print(f"动作不支持: {e}")

try:
    # API通用异常
    devices = api.get_devices_list()
except APIError as e:
    print(f"API调用失败: {e}")
```

::: tip
完整的异常类型和错误码请参考 [异常与错误码](/reference/errors)。
:::
