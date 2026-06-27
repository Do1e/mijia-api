# MCP Server

`mijiaAPI` 提供了 MCP (Model Context Protocol) server，可以让 LLM（如 Claude）直接控制米家设备，无需编写代码。

## 前置准备

MCP server 走 stdio 协议，无法在终端打印二维码，因此需要先通过 CLI 完成登录：

```bash
# 首次登录（会在终端打印二维码，用米家APP扫描）
uvx mijiaAPI login

# 或指定认证文件路径
uvx mijiaAPI login -p /path/to/auth.json
```

登录后认证数据会保存，MCP server 启动时会自动检查并复用，token 失效时自动刷新。

## 启动 MCP server

```bash
uvx mijiaAPI mcp

# 或指定认证文件路径
uvx mijiaAPI mcp -p /path/to/auth.json
```

若未登录或认证已失效，server 会立即退出并提示先运行 `mijiaAPI login`。

## 客户端配置

在 MCP 客户端（如 Claude Desktop、Cursor）的配置文件中添加：

```json
{
  "mcpServers": {
    "mijia-api": {
      "command": "uvx",
      "args": ["mijiaAPI", "mcp"]
    }
  }
}
```

指定认证文件路径时：

```json
{
  "mcpServers": {
    "mijia-api": {
      "command": "uvx",
      "args": ["mijiaAPI", "mcp", "-p", "/path/to/auth.json"]
    }
  }
}
```

## 可用工具

MCP server 暴露以下工具供 LLM 调用：

| 工具 | 说明 |
|------|------|
| `list_homes` | 列出所有家庭及房间信息 |
| `list_devices` | 列出设备列表（含共享设备），可按家庭过滤 |
| `list_scenes` | 列出手动场景，可按家庭过滤 |
| `list_consumables` | 列出耗材信息，可按家庭过滤 |
| `get_device_spec` | 获取设备规格（属性和动作列表），用于确定可用参数名 |
| `get_device_properties` | 获取设备属性值（高层封装，按属性名读取，无需 siid/piid） |
| `set_device_property` | 设置设备属性值（高层封装，按属性名写入） |
| `run_device_action` | 执行设备动作（高层封装，按动作名执行） |
| `run_scene` | 运行手动场景（按 ID 或名称） |
| `get_statistics` | 获取设备统计数据（如耗电量） |
| `run_speaker_command` | 通过小爱音箱执行自然语言指令 |

## 典型用法

先用 `list_devices` 获取设备，用 `get_device_spec` 查询设备支持的属性/动作名，再用 `get_device_properties` / `set_device_property` / `run_device_action` 控制设备。
