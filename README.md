# mijiaAPI

小米米家设备的API，可以使用代码直接控制米家设备。

[![GitHub](https://img.shields.io/badge/GitHub-Do1e%2Fmijia--api-blue)](https://github.com/Do1e/mijia-api)
[![PyPI](https://img.shields.io/badge/PyPI-mijiaAPI-blue)](https://pypi.org/project/mijiaAPI/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](https://opensource.org/licenses/GPL-3.0)

## ⚠️ 重要提醒

**v1.5.0 和 v3.0.0包含多项破坏性变更！**

如果您正在从旧版本升级，请务必查看 [CHANGELOG.md](CHANGELOG.md) 以了解详细的变更内容和迁移指南。

常见问题见 [FAQ.md](FAQ.md)。

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install mijiaAPI
```

### 从源码安装

```bash
git clone https://github.com/Do1e/mijia-api.git
cd mijia-api
pip install .
# Or `pip install -e .` for editable mode
# Or `uv sync` for uv users
```

### aur
如果你使用 Arch Linux 或基于 Arch 的发行版，可以通过 AUR 安装：

```bash
yay -S python-mijia-api
```

## 使用

### 登录

#### 扫码登录

首次使用需要通过二维码登录，认证数据将被保存以便后续使用：

```python
from mijiaAPI import mijiaAPI

# 初始化API（认证文件默认保存在 ~/.config/mijia-api/auth.json）
api = mijiaAPI()

# 或指定自定义路径
# api = mijiaAPI(".mijia-api-data/auth.json")

# 登录（如果Token有效会自动跳过）
api.login()  # 使用二维码登录
```

登录时会在终端打印二维码，使用米家APP扫描即可完成身份验证。

### API 基础使用

#### 1. 获取家庭和设备列表

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

#### 2. 获取和设置设备属性

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

#### 3. 执行设备动作

```python
# 执行设备动作（如开关灯的切换动作）
result = api.run_action({
    "did": "device_did",
    "siid": 2,
    "aiid": 1
})
```

#### 4. 场景控制

```python
# 获取场景列表
scenes = api.get_scenes_list()

# 执行场景
result = api.run_scene(scene_id="scene_id", home_id="home_id")
```

#### 5. 耗材管理

```python
# 获取耗材列表（如滤芯、灯泡等）
consumables = api.get_consumable_items()

# 获取指定家庭的耗材
consumables_in_home = api.get_consumable_items(home_id=home_id)
```

#### 6. 统计数据

```python
# 获取设备统计数据（如耗电量）
import time

result = api.get_statistics({
    "did": "device_did",
    "key": "7.1",                    # siid.piid
    "data_type": "stat_month_v3",    # 统计类型：stat_hour_v3, stat_day_v3, stat_week_v3, stat_month_v3
    "limit": 6,                      # 返回的最大条目数
    "time_start": int(time.time() - 30*24*3600),
    "time_end": int(time.time()),
})

for item in result:
    print(f"时间: {item['time']}, 数值: {item['value']}")
```

### 设备信息获取

使用 `get_device_info()` 函数可从[米家规格平台](https://home.miot-spec.com/)在线获取设备属性和动作信息：

```python
from mijiaAPI import get_device_info

# 获取设备规格信息
device_info = get_device_info('yeelink.light.lamp4')  # 米家台灯 1S 的 model

# 查看设备支持的属性和动作
print(device_info)
```

### 高级使用：mijiaDevice 类

`mijiaDevice` 类提供了一个高级封装，让您可以像操作普通对象一样控制设备，而无需关心 siid/piid 的细节：

#### 初始化设备

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

#### 获取和设置属性

```python
# 获取属性值
brightness = device.get('brightness')
print(f"当前亮度: {brightness}%")

# 设置属性值
device.set('brightness', 60)      # 设置亮度为60%
device.set('on', True)            # 打开设备
device.set('color-temperature', 5000)  # 设置色温
```

也可以直接使用属性值赋值的方式，包含"-"的属性名请使用下划线"_"替代：

```python
print(f"当前亮度: {device.brightness}%")
device.brightness = 60  # 设置亮度为60%
device.on = True        # 打开设备
device.color_temperature = 5000  # 设置色温
```

#### 执行设备动作

```python
# 执行动作（如切换开关）
device.run_action('toggle')
```

#### 查看设备属性和动作列表

```python
# 查看所有支持的属性
for prop_name, prop_obj in device.prop_list.items():
    print(f"属性: {prop_name} ({prop_obj.desc})")
    print(f"  类型: {prop_obj.type}, 读写: {prop_obj.rw}, 单位: {prop_obj.unit}")

# 查看所有支持的动作
for action_name, action_obj in device.action_list.items():
    print(f"动作: {action_name} ({action_obj.desc})")
```


### 异常处理

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

### Mijia API CLI

`mijiaAPI` 提供了命令行工具，可以直接在终端中控制米家设备，无需编写Python代码。

#### 主命令帮助

```bash
mijiaAPI --help
```

完整的命令行参数说明：

```
usage: mijiaAPI [-h] [-p AUTH_PATH] [--list_homes] [-l] [--list_scenes] 
                 [--list_consumable_items] [--run_scene SCENE_ID/SCENE_NAME ...] 
                 [--get_device_info DEVICE_MODEL] [--run PROMPT] 
                 [--wifispeaker_name WIFISPEAKER_NAME] [--quiet]
                 {get,set} ...

positional arguments:
  {get,set}
    get                 获取设备属性
    set                 设置设备属性

options:
  -h, --help            show this help message and exit
  -v, --version         显示版本信息并退出
  -p, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json
  --list_homes          列出家庭列表
  -l, --list_devices    列出所有米家设备，包含共享设备
  --list_scenes         列出场景列表
  --list_consumable_items
                        列出耗材列表
  --run_scene SCENE_ID/SCENE_NAME [SCENE_ID/SCENE_NAME ...]
                        运行场景，指定场景ID或名称
  --get_device_info DEVICE_MODEL
                        获取设备信息，指定设备model，先使用 --list_devices 获取
  --run PROMPT          使用自然语言描述你的需求，如果你有小爱音箱的话
  --wifispeaker_name WIFISPEAKER_NAME
                        指定小爱音箱名称，默认是获取到的第一个小爱音箱
  --quiet               小爱音箱静默执行
```

```
usage: mijiaAPI get [-h] [-p AUTH_PATH] [--did DID] [--dev_name DEV_NAME] --prop_name PROP_NAME

options:
  -h, --help            show this help message and exit
  -p, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json
  --did DID             设备did，优先于 --dev_name 使用
  --dev_name DEV_NAME   设备名称，指定为米家APP中设定的名称
  --prop_name PROP_NAME
                        属性名称，先使用 --get_device_info 获取
```

```
usage: mijiaAPI set [-h] [-p AUTH_PATH] [--did DID] [--dev_name DEV_NAME] --prop_name PROP_NAME --value VALUE

options:
  -h, --help            show this help message and exit
  -p, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json
  --did DID             设备did，优先于 --dev_name 使用
  --dev_name DEV_NAME   设备名称，指定为米家APP中设定的名称
  --prop_name PROP_NAME
                        属性名称，先使用 --get_device_info 获取
  --value VALUE         需要设定的属性值
```

#### 获取设备属性

```bash
# 查看帮助
mijiaAPI get --help

# 获取设备属性
mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"

# 指定认证文件路径
mijiaAPI -p /path/to/auth.json get --dev_name "卧室台灯" --prop_name "on"
```

#### 设置设备属性

```bash
# 查看帮助
mijiaAPI set --help

# 设置设备属性
mijiaAPI set --dev_name "卧室台灯" --prop_name "brightness" --value 60

# 打开设备
mijiaAPI set --dev_name "卧室台灯" --prop_name "on" --value True
```

#### 常用命令示例

```bash
# 列出所有设备（首先需要这个来获取设备名称）
mijiaAPI -l

# 列出所有家庭
mijiaAPI --list_homes

# 列出所有场景
mijiaAPI --list_scenes

# 执行场景
mijiaAPI --run_scene "睡眠模式" "晚安"

# 获取设备规格信息
mijiaAPI --get_device_info yeelink.light.lamp4

# 列出耗材
mijiaAPI --list_consumable_items

# 使用小爱音箱执行自然语言命令
mijiaAPI --run "打开卧室台灯"
mijiaAPI --run "把亮度调到50%" --wifispeaker_name "卧室小爱"
mijiaAPI --run "关闭所有灯" --quiet
```

#### 直接使用 uvx（无需安装）

如果安装了 `uv` 工具，可以直接使用 `uvx` 运行，无需提前安装 `mijiaAPI`：

```bash
uvx mijiaAPI --help
uvx mijiaAPI -l
uvx mijiaAPI get --dev_name "台灯" --prop_name "brightness"
```

### 最佳实践

#### 设置 sleep_time 参数

在使用 `mijiaDevice` 时，可以设置 `sleep_time` 参数来控制获取属性值时的等待时间。某些设备可能响应较慢，增加此参数可以获取更准确的值：

```python
# 默认 sleep_time 为 0.5 秒
device = mijiaDevice(api, dev_name="我的设备", sleep_time=1.0)

# 获取属性时会自动等待指定的时间
value = device.get('brightness')
```

#### 查询设备规格信息

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

#### 使用正确的认证文件路径

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

#### 批量操作性能优化

对多个设备进行操作时，建议使用批量操作而不是逐个操作：

```python
# 低效方式：逐个获取
for device_id in device_ids:
    result = api.get_devices_prop({"did": device_id, "siid": 2, "piid": 2})

# 高效方式：批量获取
props_list = [{"did": device_id, "siid": 2, "piid": 2} for device_id in device_ids]
results = api.get_devices_prop(props_list)
```

#### 查看debug日志

如果遇到问题，可以启用 debug 日志来了解详细的API调用过程：

```python
import logging

# 启用 debug 日志
logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

# 现在所有 API 调用都会打印详细的日志
api = mijiaAPI()
api.login()
```

## 致谢

* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)
* [米家 APP 网络请求的抓包、加解密与构造的代码笔记](https://imkero.net/posts/mihome-app-api/)
* [al-one/hass-xiaomi-miot](https://github.com/al-one/hass-xiaomi-miot)

## 开源许可

本项目采用 [GPL-3.0](LICENSE) 开源许可证。

## 免责声明

* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除
* 用户使用本项目所产生的任何后果，需自行承担风险
* 开发者不对使用本项目产生的任何直接或间接损失负责
