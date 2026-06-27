# CLI 命令行

`mijiaAPI` 提供了命令行工具，可以直接在终端中控制米家设备，无需编写 Python 代码。

## 主命令帮助

```bash
mijiaAPI --help
```

## 环境变量

支持以下环境变量来配置 CLI 的行为：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MIJIA_LOG_LEVEL` | `INFO` | 日志级别，可选值：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### 示例

```bash
# 设置为 DEBUG 级别查看详细日志
export MIJIA_LOG_LEVEL=DEBUG
mijiaAPI --list_devices

# 或直接在命令前指定
MIJIA_LOG_LEVEL=WARNING mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"
```

## 子命令

CLI 包含以下子命令：

| 子命令 | 说明 |
|--------|------|
| `login` | 二维码登录米家账号 |
| `get` | 获取设备属性 |
| `set` | 设置设备属性 |
| `run` | 使用自然语言描述需求（通过小爱音箱执行） |
| `mcp` | 启动 MCP server（stdio 传输） |

## 获取设备属性

```bash
# 查看帮助
mijiaAPI get --help

# 获取设备属性
mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"

# 指定认证文件路径
mijiaAPI -p /path/to/auth.json get --dev_name "卧室台灯" --prop_name "on"
```

## 设置设备属性

```bash
# 查看帮助
mijiaAPI set --help

# 设置设备属性
mijiaAPI set --dev_name "卧室台灯" --prop_name "brightness" --value 60

# 打开设备
mijiaAPI set --dev_name "卧室台灯" --prop_name "on" --value True
```

## 常用命令示例

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
mijiaAPI run "打开卧室台灯"
mijiaAPI run "把亮度调到50%" --wifispeaker_name "卧室小爱"
mijiaAPI run "关闭所有灯" --quiet
```

## 直接使用 uvx（无需安装）

如果安装了 `uv` 工具，可以直接使用 `uvx` 运行，无需提前安装 `mijiaAPI`：

```bash
uvx mijiaAPI --help
uvx mijiaAPI -l
uvx mijiaAPI get --dev_name "台灯" --prop_name "brightness"
```

::: tip
完整的命令行参数说明请参考 [CLI 参数参考](/reference/cli-args)。
:::
