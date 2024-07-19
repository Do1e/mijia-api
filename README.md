# mijiaAPI
小米米家设备的api，可以使用代码直接控制米家设备的功能

## 安装
```bash
python setup.py install
```
或者
```bash
pip install mijiaAPI
```

## 使用
使用实例可以参考`demos`文件夹下的示例代码，以下是简单的使用说明

有两个类分别用于登录和API调用

* `mijiaLogin`：登录小米账号，获取控制设备必须的`userId`, `ssecurity`, `deviceId`, `serviceToken`，方法列表
  * `login(username: str, password: str) -> dict`：账号密码登录，返回上述信息
  * `QRlogin() -> dict`：扫描二维码登录，返回上述信息（会在支持tty的终端打印二维码，若打印识别可查看当前文件夹下的`qr.png`）

* `mijiaAPI`：API的实现，使用`mijiaLogin`登录后返回的信息进行初始化
  * `__init__(self, auth_data: dict)`：初始化
  * `get_devices_list() -> list`：获取设备列表
  * `get_homes_list() -> list`：获取家庭列表，家庭字典中包含房间列表
  * `get_scenes_list(home_id: str) -> list`：获取手动场景列表，在 *米家->添加->手动控制* 中设置
  * `run_scene(scene_id: str) -> bool`：运行手动场景
  * `get_consumable_items(did: str) -> list`：获取设备的耗材信息，`did`为设备id，在设备列表中获取
  * `get_devices_prop(data: list) -> list`：获取设备的属性
  * `set_devices_prop(data: list) -> list`：设置设备的属性
    * ，`data`为一个字典的列表，字典需要包含`did`, `siid`, `piid`，后面两个键可从 *https://home.miot-spec.com/spec/{model}* 中获取，其中`model`为设备的model，在设备列表中获取，如[米家台灯 1S](https://home.miot-spec.com/spec/yeelink.light.lamp4)

## 致谢
* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)

## 声明
* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除。
* 本项目作者不对使用本项目产生的任何后果负责，请用户自行承担使用本项目的风险。
