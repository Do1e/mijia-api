# 快速开始

本页将带你完成 mijiaAPI 的基本使用流程：登录 → 获取设备 → 控制设备。

## 登录

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

::: tip
用于访问 API 的 `serviceToken` 有效期较短，但已实现自动刷新。用于刷新的 `passToken` 有效期约为一个月，即扫码登录后理论上可以保活一个月，实际上会更长。
:::

## 获取设备列表

```python
from mijiaAPI import mijiaAPI

api = mijiaAPI()
api.login()

# 获取所有设备（包含共享设备）
devices = api.get_devices_list()
for device in devices:
    print(f"设备名称: {device['name']}, Model: {device['model']}, Did: {device['did']}")
```

## 控制设备（推荐方式）

使用 `mijiaDevice` 类可以像操作普通对象一样控制设备，无需关心 siid/piid：

```python
from mijiaAPI import mijiaAPI, mijiaDevice

api = mijiaAPI()
api.login()

# 通过设备名称初始化（推荐，更人性化）
device = mijiaDevice(api, dev_name="我的台灯")

# 获取属性值
print(f"当前亮度: {device.brightness}%")

# 设置属性值
device.on = True              # 打开设备
device.brightness = 60        # 设置亮度为 60%
device.color_temperature = 5000  # 设置色温

# 执行动作
device.run_action('toggle')

# 查看设备支持的所有属性和动作
print(device)
```

::: tip
包含 `-` 的属性名请使用下划线 `_` 替代，例如 `color-temperature` 对应 `device.color_temperature`。
:::

## CLI 命令行

也可以直接使用命令行工具控制设备：

```bash
# 扫码登录
mijiaAPI login

# 列出所有设备
mijiaAPI -l

# 设置设备属性
mijiaAPI set --dev_name "台灯" --prop_name "brightness" --value 60

# 使用 uvx 免安装运行
uvx mijiaAPI -l
```

## 下一步

- [API 基础使用](/usage/basic-api) — 了解 siid/piid 原始调用方式
- [mijiaDevice 高级封装](/usage/mijia-device) — 深入了解面向对象的设备控制
- [CLI 命令行](/usage/cli) — 完整的 CLI 参数说明
- [MCP Server](/usage/mcp) — 让 LLM 控制你的设备
