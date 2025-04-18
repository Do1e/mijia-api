# mijiaAPI
小米米家设备的api，可以使用代码直接控制米家设备的功能，[Github link](https://github.com/Do1e/mijia-api)，[PyPI link](https://pypi.org/project/mijiaAPI/)。

## 安装
```bash
poetry install
```
或者
```bash
pip install mijiaAPI
```

## 使用
使用实例可以参考`demos`文件夹下的示例代码，以下是简单的使用说明

有三个类分别用于登录和API调用

* `mijiaLogin`：登录小米账号，获取控制设备必须的`userId`, `ssecurity`, `deviceId`, `serviceToken`，方法列表
  * `login(username: str, password: str) -> dict`：账号密码登录，返回上述信息。<span style="color:#dd4f4e">注意，目前这一方法大概率遇到手机验证码，请尽可能使用`QRlogin`。</span>
  * `QRlogin() -> dict`：扫描二维码登录，返回上述信息（会在支持tty的终端打印二维码，若打印识别可查看当前文件夹下的`qr.png`）

* `mijiaAPI`：API的实现，使用`mijiaLogin`登录后返回的信息进行初始化
  * `__init__(auth_data: dict)`：初始化
  * `available -> bool`：传入的`auth_data`是否有效
  * `get_devices_list() -> list`：获取设备列表
  * `get_homes_list() -> list`：获取家庭列表，家庭字典中包含房间列表
  * `get_scenes_list(home_id: str) -> list`：获取手动场景列表，在 *米家->添加->手动控制* 中设置
  * `run_scene(scene_id: str) -> bool`：运行手动场景
  * `get_consumable_items(home_id: str) -> list`：获取设备的耗材信息
  * `get_devices_prop(data: list) -> list`：获取设备的属性
  * `set_devices_prop(data: list) -> list`：设置设备的属性
    * `data`为一个字典的列表，字典需要包含`did`, `siid`, `piid`，后面两个键可从 *https://home.miot-spec.com/spec/{model}* 中获取，其中`model`为设备的model，在设备列表中获取，如[米家台灯 1S](https://home.miot-spec.com/spec/yeelink.light.lamp4)。
    * 网站上的方法并非全部可用，需要自行测试
  * `run_action(data: dict) -> dict`：执行设备的action
    * `data`为一个字典，需要包含`did`, `siid`, `aiid`，获取方法同上


* `mijiaDevices`：使用`mijiaAPI`和设备属性字典初始化，以便更方便地调用设备属性
  * `__init__(api: mijiaAPI, dev_info: dict. did: str = None, sleep_time: float = 0.5)`：初始化，`dev_info`为设备属性，参考[demos/dev_info_example](demos/dev_info_example)，`sleep_time`为每次调用设备属性的间隔时间（注：设置属性后立刻获取属性会不符合预期，需要延迟一段时间）
  * `set(name: str, did: str, value: Union[bool, int]) -> Union[bool, int]`：设置设备属性
  * `get(name: str, did: str) -> Union[bool, int]`：获取设备属性
  * v1.2.0 新增直接通过名称设置/获取属性，需要在初始化时传入`did`，详见[demos/test_devices_v2_light.py](demos/test_devices_v2_light.py)。名称中包含`-`的属性需要替换为`_`。
  * **欢迎大家把自己编写的设备属性字典分享到Issues中，方便大家使用**
  * 也可以调用`get_device_info(device_model: str) -> dict`函数从[米家设备列表](https://home.miot-spec.com/)在线获取设备属性字典，详见[demos/test_get_device_info.py](demos/test_get_device_info.py)

## 致谢
* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)

## 声明
* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除。
* 本项目作者不对使用本项目产生的任何后果负责，请用户自行承担使用本项目的风险。
