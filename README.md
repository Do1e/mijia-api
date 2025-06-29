# mijiaAPI

小米米家设备的API，可以使用代码直接控制米家设备。

[![GitHub](https://img.shields.io/badge/GitHub-Do1e%2Fmijia--api-blue)](https://github.com/Do1e/mijia-api)
[![PyPI](https://img.shields.io/badge/PyPI-mijiaAPI-blue)](https://pypi.org/project/mijiaAPI/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](https://opensource.org/licenses/GPL-3.0)

## ⚠️ 重要提醒

**自 v1.5.0 版本以来，本项目包含多项破坏性变更！**

如果您正在从旧版本升级，请务必查看 [CHANGELOG.md](CHANGELOG.md) 以了解详细的变更内容和迁移指南。

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
```

或者使用 poetry：

```bash
poetry install
```

### aur
如果你使用 Arch Linux 或基于 Arch 的发行版，可以通过 AUR 安装：

```bash
yay -S python-mijia-api
```

## 使用

使用实例可以参考 `demos` 文件夹下的示例代码，以下是基本使用说明。

### 登录

`mijiaLogin`：登录小米账号，获取控制设备必须的 `userId`, `ssecurity`, `deviceId`, `serviceToken` 等信息。

#### 登录方法：

* `QRlogin() -> dict`：扫描二维码登录（推荐）
  - 在支持 tty 的终端直接显示二维码
  - 或在当前目录查看生成的 `qr.png` 文件
  
* `login(username: str, password: str) -> dict`：账号密码登录
  - **注意：此方法大概率需要手机验证码验证，建议优先使用二维码登录**


### API

`mijiaAPI`：核心API实现，使用 `mijiaLogin` 登录后返回的信息进行初始化。

#### 初始化与状态检查：

* `__init__(auth_data: dict)`：初始化 API 对象
  - `auth_data` 必须包含 `userId`, `deviceId`, `ssecurity`, `serviceToken` 四个字段

* `available -> bool`：检查传入的 `auth_data` 是否有效，根据 `auth_data` 中的 `expireTime` 字段判断

#### 设备与场景获取与控制：

下述方法可参考 [demos/test_apis.py](demos/test_apis.py) 中的示例。

* `get_devices_list() -> list`：获取设备列表
* `get_homes_list() -> list`：获取家庭列表（包含房间信息）
* `get_scenes_list(home_id: str) -> list`：获取手动场景列表
  - 在米家 App 中通过 **米家→添加→手动控制** 设置
* `run_scene(scene_id: str) -> bool`：运行指定场景
* `get_consumable_items(home_id: str, owner_id: Optional[int] = None) -> list`：获取设备的耗材信息，如果是共享家庭，需要额外指定 `owner_id` 参数
* `get_devices_prop(data: list) -> list`：获取设备属性
* `set_devices_prop(data: list) -> list`：设置设备属性
* `run_action(data: dict) -> dict`：执行设备的特定动作
* `get_statistics(data: dict) -> list`：获取设备的统计信息，如空调每个月的耗电量，参考 [demos/test_get_statistics.py](demos/test_get_statistics.py)

设备属性和动作的相关参数（`siid`, `piid`, `aiid`）可以从 [米家产品库](https://home.miot-spec.com) 查询：
* 访问 `https://home.miot-spec.com/spec/{model}`（`model` 在设备列表中获取）
* 例如：[米家台灯 1S](https://home.miot-spec.com/spec/yeelink.light.lamp4)

**注意**：并非所有米家产品库中列出的方法都可用，需要自行测试验证。

### 设备信息获取

使用 `get_device_info()` 函数可从米家规格平台在线获取设备属性字典：

```python
from mijiaAPI import get_device_info

# 获取设备规格信息
device_info = get_device_info('yeelink.light.lamp4')  # 米家台灯 1S 的 model
```

详细示例：[demos/test_get_device_info.py](demos/test_get_device_info.py)

### 设备控制封装

`mijiaDevice`：基于 `mijiaAPI` 的高级封装，提供更简便的设备控制方式。

#### 初始化：

```python
mijiaDevice(api: mijiaAPI, dev_info: dict = None, dev_name: str = None, did: str = None, sleep_time: float = 0.5)
```

* `api`：已初始化的 `mijiaAPI` 对象
* `dev_info`：设备属性字典（可选）
  - 可通过 `get_device_info()` 函数获取
  - **注意**：如果提供了 `dev_info`，则不需要提供 `dev_name`
* `dev_name`：设备名称，用于自动查找设备（可选）
  - 例如：`dev_name='台灯'`，会自动查找名称包含“台灯”的设备
  - **注意**：如果提供了 `dev_name`，则不需要提供 `dev_info` 和 `did`
* `did`：设备ID，便于直接通过属性名访问（可选）
  - 如果初始化时未提供，无法使用属性样式访问，需要使用 `get()` 和 `set()` 方法指定 `did`
  - 使用 `dev_name` 初始化时，`did` 会自动获取
* `sleep_time`：属性操作间隔时间，单位秒（默认0.5秒）
  - **重要**：设置属性后立即获取可能不符合预期，需设置适当延迟

#### 使用方法控制：

* `set(name: str, value: Union[bool, int, float, str], did: Optional[str] = None) -> bool`：设置设备属性
* `get(name: str, did: Optional[str] = None) -> Union[bool, int, float, str]`：获取设备属性
* `run_action(name: str, did: Optional[str] = None, value: Optional[Union[list, tuple]] = None, **kwargs) -> bool`：执行设备动作

#### 属性样式访问：

需在初始化时提供 `did` 或者使用 `dev_name` 初始化

```python
# 示例：控制台灯
device = mijiaDevice(api, dev_name='台灯')
device.on = True                 # 打开灯
device.brightness = 60           # 设置亮度
current_temp = device.color_temperature  # 获取色温
```

属性名规则：使用下划线替代连字符（如 `color-temperature` 变为 `color_temperature`）

#### 示例：

* 使用自然语言让小爱音箱执行：[demos/test_devices_wifispeaker.py](demos/test_devices_wifispeaker.py)
* 通过属性直接控制台灯：[demos/test_devices_v2_light.py](demos/test_devices_v2_light.py)

### Mijia API CLI
`mijiaAPI` 还提供了一个命令行工具，可以直接在终端中使用。

```
> python -m mijiaAPI --help
> mijiaAPI --help
usage: mijiaAPI [-h] [-p AUTH_PATH] [-l] [--list_homes] [--list_scenes] [--list_consumable_items]
                [--run_scene SCENE_ID/SCENE_NAME [SCENE_ID/SCENE_NAME ...]] [--get_device_info DEVICE_MODEL] [--run PROMPT]
                [--wifispeaker_name WIFISPEAKER_NAME] [--quiet]
                {get,set} ...

Mijia API CLI

positional arguments:
  {get,set}
    get                 获取设备属性
    set                 设置设备属性

options:
  -h, --help            show this help message and exit
  -p AUTH_PATH, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在~/.config/mijia-api-auth.json
  -l, --list_devices    列出所有米家设备
  --list_homes          列出家庭列表
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
> python -m mijiaAPI get --help
> mijiaAPI get --help
usage: __main__.py get [-h] [-p AUTH_PATH] --dev_name DEV_NAME --prop_name PROP_NAME

options:
  -h, --help            show this help message and exit
  -p AUTH_PATH, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在~/.config/mijia-api-auth.json
  --dev_name DEV_NAME   设备名称，指定为米家APP中设定的名称
  --prop_name PROP_NAME
                        属性名称，先使用 --get_device_info 获取
```

```
> python -m mijiaAPI set --help
> mijiaAPI set --help
usage: __main__.py set [-h] [-p AUTH_PATH] --dev_name DEV_NAME --prop_name PROP_NAME --value VALUE

options:
  -h, --help            show this help message and exit
  -p AUTH_PATH, --auth_path AUTH_PATH
                        认证文件保存路径，默认保存在~/.config/mijia-api-auth.json
  --dev_name DEV_NAME   设备名称，指定为米家APP中设定的名称
  --prop_name PROP_NAME
                        属性名称，先使用 --get_device_info 获取
  --value VALUE         需要设定的属性值
```

或者直接使用`uvx`忽略安装步骤：

```bash
uvx mijiaAPI --help
```

#### 示例：

```bash
mijiaAPI -l # 列出所有米家设备
mijiaAPI --list_homes # 列出家庭列表
mijiaAPI --list_scenes # 列出场景列表
mijiaAPI --list_consumable_items # 列出耗材列表
mijiaAPI --run_scene SCENE_ID/SCENE_NAME # 运行场景，指定场景ID或名称
mijiaAPI --get_device_info DEVICE_MODEL # 获取设备信息，指定设备model，先使用 --list_devices 获取
mijiaAPI get --dev_name DEV_NAME --prop_name PROP_NAME # 获取设备属性
mijiaAPI set --dev_name DEV_NAME --prop_name PROP_NAME --value VALUE # 设置设备属性
mijiaAPI --run 明天天气如何
mijiaAPI --run 打开台灯并将亮度调至最大 --quiet
```

## 致谢

* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)

## 开源许可

本项目采用 [GPL-3.0](LICENSE) 开源许可证。

## 免责声明

* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除
* 用户使用本项目所产生的任何后果，需自行承担风险
* 开发者不对使用本项目产生的任何直接或间接损失负责
