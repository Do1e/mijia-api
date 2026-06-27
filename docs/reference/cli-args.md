# CLI 参数参考

## 安装

## 从 uv 安装（推荐）

使用 [uv](https://docs.astral.sh/uv/) 以独立工具方式安装，无需管理虚拟环境，`mijiaAPI` 命令全局可用：

```bash
uv tool install mijiaAPI
```

## AUR（Arch User Repository）

如果你使用 Arch Linux 或基于 Arch 的发行版，可以通过 AUR 安装：

```bash
yay -S python-mijia-api
```

## 主命令

```
usage: mijiaAPI [-h] [-v] [-p AUTH_PATH] [--list_homes] [-l]
                   [--list_scenes] [--list_consumable_items]
                   [--run_scene SCENE_ID/SCENE_NAME [SCENE_ID/SCENE_NAME ...]]
                   [--get_device_info DEVICE_MODEL]
                   {run,get,set,mcp,login} ...
```

### 全局参数

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息并退出 |
| `-v, --version` | 显示版本信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径，默认 `~/.config/mijia-api/auth.json` |
| `--list_homes` | 列出家庭列表 |
| `-l, --list_devices` | 列出所有米家设备，包含共享设备 |
| `--list_scenes` | 列出场景列表 |
| `--list_consumable_items` | 列出耗材列表 |
| `--run_scene SCENE_ID/SCENE_NAME [...]` | 运行场景，指定场景ID或名称（可多个） |
| `--get_device_info DEVICE_MODEL` | 获取设备信息，指定设备 model |

### 环境变量

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MIJIA_LOG_LEVEL` | `INFO` | 日志级别，可选值：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## 子命令：login

二维码登录米家账号。

```
usage: mijiaAPI login [-h] [-p AUTH_PATH]
```

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径 |

`login` 子命令会尝试刷新 token；若仍不可用则在终端打印二维码并阻塞等待扫码。其他子命令（`get`/`set`/`run`/`mcp` 及全局参数）在认证文件缺失、损坏或失效且刷新失败时，**不会**自动触发登录，而是打印 `请调用 'mijiaAPI login' 进行扫描登录` 并以退出码 1 退出。

## 子命令：get

获取设备属性。

```
usage: mijiaAPI get [-h] [-p AUTH_PATH] [--did DID] [--dev_name DEV_NAME] --prop_name PROP_NAME
```

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径 |
| `--did DID` | 设备 did，优先于 `--dev_name` 使用 |
| `--dev_name DEV_NAME` | 设备名称，指定为米家APP中设定的名称 |
| `--prop_name PROP_NAME` | 属性名称（必填），先使用 `--get_device_info` 获取 |

## 子命令：set

设置设备属性。

```
usage: mijiaAPI set [-h] [-p AUTH_PATH] [--did DID] [--dev_name DEV_NAME] --prop_name PROP_NAME --value VALUE
```

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径 |
| `--did DID` | 设备 did，优先于 `--dev_name` 使用 |
| `--dev_name DEV_NAME` | 设备名称，指定为米家APP中设定的名称 |
| `--prop_name PROP_NAME` | 属性名称（必填），先使用 `--get_device_info` 获取 |
| `--value VALUE` | 需要设定的属性值（必填） |

## 子命令：run

使用自然语言描述你的需求，通过小爱音箱执行。

```
usage: mijiaAPI run [-h] [-p AUTH_PATH]
                       [--wifispeaker_name WIFISPEAKER_NAME] [--quiet]
                       PROMPT
```

| 参数 | 说明 |
|------|------|
| `PROMPT` | 使用自然语言描述你的需求（位置参数，必填） |
| `-h, --help` | 显示帮助信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径 |
| `--wifispeaker_name WIFISPEAKER_NAME` | 指定小爱音箱名称，默认是获取到的第一个小爱音箱 |
| `--quiet` | 小爱音箱静默执行 |

## 子命令：mcp

启动 MCP server（stdio 传输）。

```
usage: mijiaAPI mcp [-h] [-p AUTH_PATH]
```

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息并退出 |
| `-p, --auth_path AUTH_PATH` | 认证文件保存路径 |
