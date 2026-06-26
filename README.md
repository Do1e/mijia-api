# mijiaAPI

小米米家设备的 API，可以使用代码直接控制米家设备。

[![GitHub](https://img.shields.io/badge/GitHub-Do1e%2Fmijia--api-blue)](https://github.com/Do1e/mijia-api)
[![PyPI](https://img.shields.io/badge/PyPI-mijiaAPI-blue)](https://pypi.org/project/mijiaAPI/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](https://opensource.org/licenses/GPL-3.0)

📖 **完整文档请见 [mijia-api.do1e.com](https://mijia-api.do1e.com)**

## 安装

> 要求 Python >= 3.10

```bash
pip install mijiaAPI
# Or `uv add mijiaAPI` for uv users
```

其他安装方式（源码安装、AUR）请参考[文档](https://mijia-api.do1e.com)。

## 快速开始

```python
from mijiaAPI import mijiaAPI, mijiaDevice

# 初始化并扫码登录（认证文件默认保存在 ~/.config/mijia-api/auth.json）
api = mijiaAPI()
api.login()

# 通过设备名称控制设备（推荐）
device = mijiaDevice(api, dev_name="我的台灯")
device.on = True              # 打开设备
device.brightness = 60        # 设置亮度为 60%

# 查看设备支持的所有属性和动作
print(device)
```

CLI 用法：

```bash
mijiaAPI login                          # 扫码登录
mijiaAPI -l                             # 列出所有设备
mijiaAPI set --dev_name "台灯" --prop_name "brightness" --value 60
```

更多用法（API 基础调用、MCP Server、CLI 完整参数、最佳实践等）请查阅[完整文档](https://mijia-api.do1e.com)。

## 致谢

* [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)
* [米家 APP 网络请求的抓包、加解密与构造的代码笔记](https://imkero.net/posts/mihome-app-api/)
* [al-one/hass-xiaomi-miot](https://github.com/al-one/hass-xiaomi-miot)

## 开源许可

本项目采用 [GPL-3.0](LICENSE) 开源许可证。

**请注意：GPL-3.0 是具有“强传染性”的开源许可证。**  
如果您在您的项目中使用、修改或分发本项目的代码（包括作为库依赖），您的整个项目也**必须**以 GPL-3.0 或兼容许可证开源发布。

## 免责声明

* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除
* 用户使用本项目所产生的任何后果，需自行承担风险
* 开发者不对使用本项目产生的任何直接或间接损失负责
