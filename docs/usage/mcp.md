# MCP Server

`mijiaAPI` 提供了 MCP (Model Context Protocol) server，可以让 LLM（如 Claude）直接控制米家设备，无需编写代码。

## 启动 MCP server

```bash
uvx mijiaAPI mcp

# 或指定认证文件路径
uvx mijiaAPI mcp -p /path/to/auth.json
```

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
| `login` | 发起米家二维码登录：先尝试刷新 token，失败则生成二维码并在后台长轮询等待扫码，返回二维码图片链接 |
| `login_status` | 查询 `login` 发起的登录结果（pending/success/error），成功后自动切换为新凭证 |
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

## 会话内登录流程

当凭证过期且自动刷新失败时，LLM 可按以下步骤在会话内完成登录，无需重启 server：

1. 调用 `login`：server 先尝试刷新 token；若仍不可用，则生成二维码，在后台线程长轮询等待扫码，并返回二维码图片链接。
2. 用户用米家APP在 2 分钟内扫描 `login` 返回的二维码图片。
3. 调用 `login_status` 查询结果：
   - `pending`：仍在等待扫码，稍后再次查询。
   - `success`：登录成功，已切换为新凭证，后续工具调用将使用新凭证。
   - `error`：登录失败，返回错误信息，可重新调用 `login`。

::: warning
`login` 不会阻塞 server——它在后台线程等待扫码，因此 LLM 在等待期间可以继续响应，但设备控制工具在登录完成前仍会失败。
:::

## 典型用法

先用 `list_devices` 获取设备，用 `get_device_spec` 查询设备支持的属性/动作名，再用 `get_device_properties` / `set_device_property` / `run_device_action` 控制设备。遇到认证失效时，按上文“会话内登录流程”调用 `login` + `login_status`。
