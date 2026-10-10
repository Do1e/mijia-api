# mijiaAPI

米家 API，可以使用代码、CLI、MCP 直接控制米家设备。

> ⚠️ **v5.0.0 兼容性说明**：设备规格数据源迁移至 [miot-spec.org](https://miot-spec.org/)（小米官方数据源），有以下破坏性变更：
>
> - `get_device_info()` 参数由 `device_model` 改为 `spec_type`（设备规格类型 URN，可从 `get_devices_list()` 返回的设备信息中获取）
> - CLI `--get_device_info` 由接收 model 改为接收 `spec_type`（可从 `-l` 输出的 `spec_type` 字段获取）
> - MCP 工具 `get_device_spec` 参数由 `device_model` 改为 `spec_type`
>
> 除上述改动外，其余用法与 v4 保持兼容。

[![GitHub](https://img.shields.io/badge/GitHub-Do1e%2Fmijia--api-blue)](https://github.com/Do1e/mijia-api)
[![PyPI](https://img.shields.io/badge/PyPI-mijiaAPI-blue)](https://pypi.org/project/mijiaAPI/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](https://opensource.org/licenses/GPL-3.0)

📖 **完整文档请见 [mijia-api.do1e.com](https://mijia-api.do1e.com)**

[常见问题](https://mijia-api.do1e.com/faq) | [更新日志](https://mijia-api.do1e.com/changelog)

## 安装

> 要求 Python >= 3.10

```bash
pip install mijiaAPI
# uv 用户可使用 `uv add mijiaAPI`
```

其他安装方式（源码安装、AUR）请参考[文档](https://mijia-api.do1e.com/guide/installation)。

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

MCP 用法：

执行 `uvx mijiaAPI login -p /path/to/auth.json` 登录后，在 MCP 客户端配置中添加以下内容即可接入米家：

```json
{
  "mcpServers": {
    "mijia-api": {
      "command": "uvx",
      "args": ["mijiaAPI[mcp]", "mcp", "-p", "/path/to/auth.json"]
    }
  }
}
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
