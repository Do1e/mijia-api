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
| `action` | 按动作名执行设备动作 |
| `statistics` | 获取设备统计数据 |
| `run` | 使用自然语言描述需求（通过小爱音箱执行） |
| `mcp` | 启动 MCP server（stdio 传输） |

## 获取设备属性

```bash
# 查看帮助
mijiaAPI get --help

# 获取设备属性
mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"

# 指定认证文件路径
mijiaAPI get -p /path/to/auth.json --dev_name "卧室台灯" --prop_name "on"
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

## 执行设备动作

```bash
# 无参数动作
mijiaAPI action --dev_name "卧室台灯" --action_name toggle

# 带参数动作，--params 必须是 JSON 对象
mijiaAPI action --did 123456 --action_name execute-text-directive --params '{"in":["打开空调",1]}'
```

动作名可通过 `--get_device_info MODEL` 获取。`--did` 和 `--dev_name` 必须且只能提供一个。

## 获取统计数据

```bash
# 默认查询最近 30 天，最多返回 6 条
mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_month_v3

# 指定条数和时间范围（Unix 时间戳，秒）
mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_day_v3 \
  --limit 30 --time_start 1700000000 --time_end 1702592000
```

统计能力、`key` 和 `data_type` 因设备型号而异；旧设备的统计类型可能不带 `_v3` 后缀。
命令原样输出 API 返回的 JSON。

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

# 执行设备动作
mijiaAPI action --dev_name "卧室台灯" --action_name toggle

# 获取统计数据
mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_month_v3

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
