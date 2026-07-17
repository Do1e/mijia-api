---
name: mijia-api
description: |
  通过 `uvx mijiaAPI` CLI 控制米家智能设备。适用于：列出米家设备/家庭/场景/耗材、
  获取或设置设备属性、执行设备动作、查询统计数据、运行场景、通过小爱音箱执行自然语言命令。
  触发词包括"控制米家设备"、"米家"、"mijia"、"列出设备"、"设置亮度"、"打开灯"、
  "执行动作"、"统计数据"、"耗电量"、"运行场景"、"小爱音箱"、"耗材"、"场景"。
allowed-tools: Bash(uvx mijiaAPI:*)
---

# mijia-api CLI

通过 `uvx mijiaAPI` 命令行工具控制米家智能设备。所有命令均通过 `uvx` 运行，
无需本地安装（首次运行时自动下载包）。CLI 实现位于 `mijiaAPI/__main__.py`。

## 行为规则（关键）

1. **绝对不要调用 `login`。** 登录流程会在终端显示二维码，并**阻塞**等待用户用手机
   扫码，会导致会话一直挂起。如果需要登录，**停止操作**并提醒用户自行执行：

   ```
   uvx mijiaAPI login -p [path]
   ```

2. **绝对不要调用 `mcp`。** 它会启动一个长时间运行的 stdio MCP server，永久阻塞。
   该命令用于在 MCP 客户端配置中作为 server 启动，不能直接调用。

3. 其他所有命令（list、get、set、action、statistics、run、run_scene、get_device_info）均为**非阻塞**，
   可以直接调用。

4. 如果任何命令以退出码 `1` 退出，并打印类似 `请调用 'mijiaAPI login' 进行扫描登录`
   的信息，说明认证文件缺失、损坏或已过期。**不要尝试自行修复**，提醒用户执行上述
   登录命令后停止。

5. 使用 `bash` 工具调用 `uvx` 命令时设置较长超时——首次运行可能需要下载包。

## 认证文件

认证文件默认路径为 `~/.config/mijia-api/auth.json`，可用 `-p /path/to/auth.json` 覆盖。

- **全局参数**（`--list_devices`、`--list_homes` 等）：`-p` 放在参数前：
  `uvx mijiaAPI -p /path --list_devices`
- **子命令**（`get`、`set`、`action`、`statistics`、`run`）：`-p` 放在子命令后：
  `uvx mijiaAPI get -p /path --dev_name "台灯" --prop_name "brightness"`

认证失效时，`init_api` 会打印提示信息并以退出码 `1` 退出，提示用户运行
`mijiaAPI login`。将该提示转达给用户——**不要自行运行 `login`**。

## 命令总览

| 命令 / 参数 | 用途 | 需要认证 | 阻塞 |
|-------------|------|----------|------|
| `login` | 二维码登录 | 否（创建认证） | **是——禁止调用** |
| `mcp` | 启动 MCP server（stdio） | 是 | **是——禁止调用** |
| `-l`、`--list_devices` | 列出所有设备（含共享） | 是 | 否 |
| `--list_homes` | 列出家庭、房间和设备 | 是 | 否 |
| `--list_scenes` | 列出各家庭场景 | 是 | 否 |
| `--list_consumable_items` | 列出各家庭耗材 | 是 | 否 |
| `--run_scene 名称/ID [...]` | 运行一个或多个场景 | 是 | 否 |
| `--get_device_info MODEL` | 按 model 获取设备规格 | **否** | 否 |
| `get` | 读取设备属性 | 是 | 否 |
| `set` | 设置设备属性 | 是 | 否 |
| `action` | 按动作名执行设备动作 | 是 | 否 |
| `statistics` | 获取设备统计数据 | 是 | 否 |
| `run` | 通过小爱音箱执行自然语言命令 | 是 | 否 |

全局参数（`--list_devices`、`--list_homes`、`--list_scenes`、`--list_consumable_items`、
`--run_scene`、`--get_device_info`）可在一次调用中**组合使用**；其中 `--get_device_info`
在认证检查之前执行，因此无需登录即可使用。

## 典型工作流

1. **列出设备**，获取设备名称和 model：
   ```
   uvx mijiaAPI -l
   ```
   输出每个设备的 `name`、`did`、`model`、`online` 状态。

2. **按 model 查看设备支持的属性和动作**（无需登录）：
   ```
   uvx mijiaAPI --get_device_info yeelink.light.lamp4
   ```
   返回 JSON，描述设备的属性和动作。用于查找 `get`/`set` 可用的 `--prop_name` 和
   `action` 可用的 `--action_name`。

3. **获取或设置**属性（按设备名称）：
   ```
   uvx mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"
   uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "brightness" --value 60
   uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "on" --value True
   ```

4. **执行设备动作**：
   ```
   uvx mijiaAPI action --dev_name "卧室台灯" --action_name toggle
   ```

5. **获取统计数据**：
   ```
   uvx mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_month_v3
   ```

## 命令详情

### 列出设备

```
uvx mijiaAPI -l
uvx mijiaAPI --list_devices
uvx mijiaAPI -p /path/to/auth.json -l
```

列出所有设备（包含共享设备），每项显示 `name`、`did`、`model`、`online` 状态。
`name` 用于 `--dev_name`，`did` 用于 `--did`。

### 列出家庭

```
uvx mijiaAPI --list_homes
```

列出家庭及其房间和房间内设备。与 `--list_devices` 组合可显示设备名称而非原始 `did`：
```
uvx mijiaAPI -l --list_homes
```

### 列出场景

```
uvx mijiaAPI --list_scenes
```

按家庭列出场景，每项显示 `name`、`scene_id`、创建时间。与 `--list_homes` 组合可避免
重复请求家庭列表：
```
uvx mijiaAPI --list_homes --list_scenes
```

### 运行场景

```
uvx mijiaAPI --run_scene "睡眠模式"
uvx mijiaAPI --run_scene 123456
uvx mijiaAPI --run_scene "晚安" "睡眠模式"
```

接受场景 **ID 或名称**（从完整场景列表中查找）。一次可运行多个场景。与
`--list_scenes` 组合可避免重复请求场景列表：
```
uvx mijiaAPI --list_scenes --run_scene "睡眠模式"
```

### 列出耗材

```
uvx mijiaAPI --list_consumable_items
```

按家庭列出耗材（如滤芯寿命、刷头磨损）。与 `--list_homes` 组合可复用家庭映射：
```
uvx mijiaAPI --list_homes --list_consumable_items
```

### 获取设备规格（无需认证）

```
uvx mijiaAPI --get_device_info yeelink.light.lamp4
```

从公开的 MIoT 规格端点获取设备规格 JSON，返回所有可用属性（含类型和约束）及动作。
**无需登录**——在认证初始化之前执行。用于在调用 `get`/`set`/`action` 前发现合法的
`--prop_name`、`--value` 和 `--action_name`。

### 获取设备属性

```
uvx mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"
uvx mijiaAPI get --did 123456 --prop_name "on"
uvx mijiaAPI get -p /path/auth.json --dev_name "台灯" --prop_name "on"
```

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `--prop_name` | **是** | 属性名（通过 `--get_device_info` 发现） |
| `--dev_name` | 二选一 | 米家 APP 中设置的设备名称 |
| `--did` | 二选一 | 设备 did（优先于 `--dev_name`） |
| `-p` | 否 | 认证文件路径 |

输出：`<设备名> (<did>) 的 <prop_name> 值为 <value>`

### 设置设备属性

```
uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "brightness" --value 60
uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "on" --value True
uvx mijiaAPI set --did 123456 --prop_name "on" --value False
```

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `--prop_name` | **是** | 属性名（通过 `--get_device_info` 发现） |
| `--value` | **是** | 设定值（字符串，如 `60`、`True`、`False`） |
| `--dev_name` | 二选一 | 米家 APP 中设置的设备名称 |
| `--did` | 二选一 | 设备 did（优先于 `--dev_name`） |
| `-p` | 否 | 认证文件路径 |

成功时输出确认信息，失败时输出 `设置 ... 失败: <错误>`。

### 执行设备动作

```
uvx mijiaAPI action --dev_name "卧室台灯" --action_name toggle
uvx mijiaAPI action --did 123456 --action_name execute-text-directive --params '{"in":["打开空调",1]}'
```

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `--action_name` | **是** | 动作名（通过 `--get_device_info` 发现） |
| `--dev_name` | 二选一 | 米家 APP 中设置的设备名称 |
| `--did` | 二选一 | 设备 did |
| `--params` | 否 | 动作参数 JSON 对象；无参数动作不要传 |
| `-p` | 否 | 认证文件路径 |

`--params` 必须是 JSON 对象。普通动作参数可传 `{"value":[2]}`；名为 Python 关键字的
字段也直接使用原名，例如 `{"in":["打开空调",1]}`。成功输出“指令已发送”。

### 获取统计数据

```
uvx mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_month_v3
uvx mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_day_v3 --limit 30 --time_start 1700000000 --time_end 1702592000
```

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `--did` | **是** | 设备 did（从 `--list_devices` 获取） |
| `--key` | **是** | 统计键，通常为 `siid.piid`，例如 `7.1` |
| `--data_type` | **是** | 统计类型，如 `stat_day_v3`、`stat_month_v3`；旧设备可能不带 `_v3` |
| `--limit` | 否 | 最大条目数，默认 `6` |
| `--time_start` | 否 | 开始 Unix 时间戳（秒），默认结束时间前 30 天 |
| `--time_end` | 否 | 结束 Unix 时间戳（秒），默认当前时间 |
| `-p` | 否 | 认证文件路径 |

统计能力和 `key` 因设备型号而异。命令原样输出 API 返回的 JSON，不要用 `eval()` 解析
其中的字符串值。

### 运行（通过小爱音箱执行自然语言）

```
uvx mijiaAPI run "打开卧室台灯"
uvx mijiaAPI run "把亮度调到50%" --wifispeaker_name "卧室小爱"
uvx mijiaAPI run "关闭所有灯" --quiet
```

将自然语言指令通过小爱音箱的 `execute-text-directive` 动作执行。未指定
`--wifispeaker_name` 时，自动选用第一个 model 包含 `xiaomi.wifispeaker` 的设备。
若未找到小爱音箱，抛出 `ValueError("未找到小爱音箱设备")`。

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `PROMPT`（位置参数） | **是** | 自然语言指令 |
| `--wifispeaker_name` | 否 | 指定小爱音箱名称 |
| `--quiet` | 否 | 静默执行（音箱不播报回复） |
| `-p` | 否 | 认证文件路径 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MIJIA_LOG_LEVEL` | `INFO` | 日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

```
MIJIA_LOG_LEVEL=DEBUG uvx mijiaAPI -l
```

## 退出码

- `0`：成功
- `1`：认证文件缺失/损坏/过期（信息中包含
  `请调用 'mijiaAPI login' 进行扫描登录`），或命令发生未处理错误。看到认证相关提示时，
  提醒用户运行 `uvx mijiaAPI login -p [path]`。
