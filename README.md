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

### 登录

`mijiaLogin`：登录小米账号，获取控制设备必须的`userId`, `ssecurity`, `deviceId`, `serviceToken`，方法列表：
* `login(username: str, password: str) -> dict`：账号密码登录，返回上述信息。**注意，目前这一方法大概率遇到手机验证码，请尽可能使用`QRlogin`。**
* `QRlogin() -> dict`：扫描二维码登录，返回上述信息（会在支持tty的终端打印二维码，若打印识别可查看当前文件夹下的`qr.png`）

**手动登录方法**

可以使用浏览器，手动获取`userId`, `ssecurity`, `deviceId`, `serviceToken`。当然我还是更推荐大家使用扫码登录，但大家也可以根据下述步骤了解如何获取这些信息。

打开浏览器访问 https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true ，会得到下述信息，复制location中的url到新的界面打开：

```text
&&&START&&&{"serviceParam":"{\"checkSafePhone\":false,\"checkSafeAddress\":false,\"lsrp_score\":0.0}","qs":"%3Fsid%3Dxiaomiio%26_json%3Dtrue","code":70016,"description":"登录验证失败","securityStatus":0,"_sign":"0psXfr43eNI0IX6q9Suk3qWbRqU=","sid":"xiaomiio","result":"error","captchaUrl":null,"callback":"https://sts.api.io.mi.com/sts","location":"https://account.xiaomi.com/fe/service/login?_json=true&sid=xiaomiio&qs=%253Fsid%253Dxiaomiio%2526_json%253Dtrue&callback=.........","pwd":0,"child":0,"desc":"登录验证失败"}
```

打开后会进入小米的登录界面（如果直接显示了`ok`，是因为保存了之前的cookie，建议使用无痕窗口重新开始上述步骤），此时需要先按下 `F12` 打开开发者工具，切换到`Network`选项卡，之后可以输入账号密码或者扫码登录。完成后页面会显示一个`ok`。

此时在网络选项卡中按下`Ctrl+F`，搜索上述所需的`userId`, `ssecurity`, `deviceId`, `serviceToken`即可。

或者筛选请求：
1. `https://sts.api.io.mi.com/sts`，其中的`set-cookie`中包含`userId`和`serviceToken`（`=`到`;`前止）。
2. `https://account.xiaomi.com/pass/serviceLoginAuth2/end`，其中的`extension-pragma`中包含`ssecurity`（`:"`到`"`前止）。
3. `https://account.xiaomi.com/identity/authStart`，其中的`cookie`中包含`deviceId`（`=`到`;`前止）。


### API

`mijiaAPI`：API的实现，使用`mijiaLogin`登录后返回的信息进行初始化
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

### 针对设备的封装

`mijiaDevices`：使用`mijiaAPI`和设备属性字典初始化，以便更方便地调用设备属性
* `__init__(api: mijiaAPI, dev_info: dict. did: str = None, sleep_time: float = 0.5)`：初始化，`dev_info`为设备属性，参考[demos/dev_info_example](demos/dev_info_example)，`sleep_time`为每次调用设备属性的间隔时间（注：设置属性后立刻获取属性会不符合预期，需要延迟一段时间）
* `set(name: str, did: str, value: Union[bool, int]) -> Union[bool, int]`：设置设备属性
* `get(name: str, did: str) -> Union[bool, int]`：获取设备属性
* v1.2.0 新增直接通过名称设置/获取属性，需要在初始化时传入`did`，详见[demos/test_devices_v2_light.py](demos/test_devices_v2_light.py)。名称中包含`-`的属性需要替换为`_`。
* 可以调用`get_device_info(device_model: str) -> dict`函数从[米家设备列表](https://home.miot-spec.com/)在线获取设备属性字典，详见[demos/test_get_device_info.py](demos/test_get_device_info.py)

## 致谢
* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)

## 声明
* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除。
* 本项目作者不对使用本项目产生的任何后果负责，请用户自行承担使用本项目的风险。
