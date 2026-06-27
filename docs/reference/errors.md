# 异常与错误码

## 异常类层级

`mijiaAPI` 定义了以下异常类：

| 异常类 | 说明 |
|--------|------|
| `LoginError` | 登录失败 |
| `APIError` | API 通用调用失败 |
| `DeviceNotFoundError` | 设备未找到 |
| `MultipleDevicesFoundError` | 找到多个匹配的设备 |
| `DeviceGetError` | 获取设备属性失败 |
| `DeviceSetError` | 设置设备属性失败 |
| `DeviceActionError` | 执行设备动作失败 |
| `GetDeviceInfoError` | 获取设备规格信息失败 |

## 异常处理示例

```python
from mijiaAPI import (
    mijiaAPI,
    mijiaDevice,
    LoginError,
    DeviceNotFoundError,
    MultipleDevicesFoundError,
    DeviceGetError,
    DeviceSetError,
    DeviceActionError,
    APIError,
)

api = mijiaAPI()

try:
    api.login()
except LoginError as e:
    print(f"登录失败: {e}")

try:
    device = mijiaDevice(api, dev_name="我的台灯")
except DeviceNotFoundError as e:
    print(f"设备未找到: {e}")
except MultipleDevicesFoundError as e:
    print(f"找到多个匹配的设备: {e}")

try:
    device.get('brightness')
except DeviceGetError as e:
    print(f"获取属性失败: {e}")
except ValueError as e:
    print(f"属性名称不支持: {e}")

try:
    device.set('brightness', 150)
except DeviceSetError as e:
    print(f"设置属性失败: {e}")

try:
    device.run_action('toggle')
except DeviceActionError as e:
    print(f"执行动作失败: {e}")

try:
    api.get_devices_list()
except APIError as e:
    print(f"API调用失败: {e}")
```

## 错误码表

以下是米家 API 返回的错误码及对应描述：

| 错误码 | 描述 |
|--------|------|
| `-10000` | 未知错误 |
| `-10001` | 服务不可用 |
| `-10002` | 参数无效 |
| `-10003` | 资源不足 |
| `-10004` | 内部错误 |
| `-10005` | 权限不足 |
| `-10006` | 执行超时 |
| `-10007` | 设备离线或者不存在 |
| `-10020` | 未授权OAuth2 |
| `-10030` | 无效的token（HTTP） |
| `-10040` | 无效的消息格式 |
| `-10050` | 无效的证书 |
| `-704000000` | 未知错误 |
| `-704010000` | 未授权（设备可能被删除） |
| `-704014006` | 没找到设备描述 |
| `-704030013` | Property不可读 |
| `-704030023` | Property不可写 |
| `-704030033` | Property不可订阅 |
| `-704040002` | Service不存在 |
| `-704040003` | Property不存在 |
| `-704040004` | Event不存在 |
| `-704040005` | Action不存在 |
| `-704040999` | 功能未上线 |
| `-704042001` | Device不存在 |
| `-704042011` | 设备离线 |
| `-704053036` | 设备操作超时 |
| `-704053100` | 设备在当前状态下无法执行此操作 |
| `-704083036` | 设备操作超时 |
| `-704090001` | Device不存在 |
| `-704220008` | 无效的ID |
| `-704220025` | Action参数个数不匹配 |
| `-704220035` | Action参数错误 |
| `-704220043` | Property值错误 |
| `-704222034` | Action返回值错误 |
| `-705004000` | 未知错误 |
| `-705004501` | 未知错误 |
| `-705201013` | Property不可读 |
| `-705201015` | Action执行错误 |
| `-705201023` | Property不可写 |
| `-705201033` | Property不可订阅 |
| `-706012000` | 未知错误 |
| `-706012013` | Property不可读 |
| `-706012015` | Action执行错误 |
| `-706012023` | Property不可写 |
| `-706012033` | Property不可订阅 |
| `-706012043` | Property值错误 |
| `-706014006` | 没找到设备描述 |
