# Agent Skill

仓库内置了 mijia-api 的 agent skill 定义（[`skills/SKILL.md`](https://github.com/Do1e/mijia-api/blob/main/skills/SKILL.md)），供 AI 助手（如 opencode、Claude Code 等）安全地通过 `uvx mijiaAPI` CLI 控制米家设备。

## Skill 是什么

Skill 是一段提供给 LLM 的“操作指南”：告诉模型哪些命令可以调用、哪些命令禁止调用、以及典型工作流。LLM 读取后会通过 bash 工具执行 `uvx mijiaAPI ...`，从而控制你的米家设备，而无需你编写 Python 代码或手动查文档。

## 前置条件

skill 通过 `uvx mijiaAPI` 调用 CLI，依赖 [uv](https://docs.astral.sh/uv/) 来按需拉取并运行 mijiaAPI，无需手动安装 Python 或 mijiaAPI。请先安装 uv：

::: code-group

```bash [macOS / Linux]
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash [Windows]
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

:::

安装后重启终端，确认 `uv --version` 可正常输出。

## 安装 Skill

### opencode

opencode 会自动加载以下目录中的 skill（`SKILL.md`），下载 [SKILL.md](https://github.com/Do1e/mijia-api/blob/main/skills/SKILL.md)到目录中即可：

- 项目内：`.opencode/skills/mijia-api/SKILL.md`
- 全局：`~/.config/opencode/skills/mijia-api/SKILL.md`

可用以下两条 curl 命令快速完成下载：

```bash
# 下载到项目内
mkdir -p .opencode/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o .opencode/skills/mijia-api/SKILL.md

# 下载到全局
mkdir -p ~/.config/opencode/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o ~/.config/opencode/skills/mijia-api/SKILL.md
```

### Claude Code

Claude Code 会从以下目录自动发现 skill（每个 skill 为 `<name>/SKILL.md`），下载 [SKILL.md](https://github.com/Do1e/mijia-api/blob/main/skills/SKILL.md) 到对应目录即可，之后可用 `/mijia-api` 斜杠命令调用：

- 项目内（随 git 共享）：`.claude/skills/mijia-api/SKILL.md`
- 全局（所有项目可用）：`~/.claude/skills/mijia-api/SKILL.md`

```bash
# 下载到项目内
mkdir -p .claude/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o .claude/skills/mijia-api/SKILL.md

# 下载到全局
mkdir -p ~/.claude/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o ~/.claude/skills/mijia-api/SKILL.md
```

### Codex

OpenAI Codex 默认从 `$CODEX_HOME/skills/`（未设置 `CODEX_HOME` 时回退到 `~/.codex/skills/`）自动发现用户级 skill；项目级可放在 `.codex/skills/` 下随仓库共享：

- 项目内：`.codex/skills/mijia-api/SKILL.md`
- 全局：`~/.codex/skills/mijia-api/SKILL.md`

```bash
# 下载到项目内
mkdir -p .codex/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o .codex/skills/mijia-api/SKILL.md

# 下载到全局
mkdir -p ~/.codex/skills/mijia-api && curl -fsSL https://raw.githubusercontent.com/Do1e/mijia-api/main/skills/SKILL.md -o ~/.codex/skills/mijia-api/SKILL.md
```

### 通用方法

如果你的 AI 助手不在上述列表中，只要它遵循“目录下放 `SKILL.md` 即自动加载”的约定，都可以用同一种方式接入：

1. 从仓库下载 [`skills/SKILL.md`](https://github.com/Do1e/mijia-api/blob/main/skills/SKILL.md)。
2. 保存到该助手对应的 skills 目录下，命名为 `mijia-api/SKILL.md`（即 `<skills 根目录>/mijia-api/SKILL.md`）。

## 行为规则（关键）

skill 对 LLM 设定了明确的边界，避免会话卡死：

1. **禁止调用 `login`**：它会在终端打印二维码并阻塞等待扫码，导致会话挂起。需要登录时，skill 会提醒你自行执行 `uvx mijiaAPI login -p [path]`。
2. **禁止调用 `mcp`**：它会启动长时间运行的 stdio MCP server，永久阻塞。该命令仅供 MCP 客户端配置使用。
3. 其余命令（`-l`/`--list_devices`、`--list_homes`、`--list_scenes`、`--list_consumable_items`、`--run_scene`、`--get_device_info`、`get`、`set`、`action`、`statistics`、`run`）均为非阻塞，可直接调用。
4. 当命令以退出码 1 退出并提示 `请调用 'mijiaAPI login' 进行扫描登录` 时，说明认证缺失/损坏/过期，模型会转告你执行登录命令而非自行修复。

::: tip
若希望 LLM 能在会话内完成登录而不打断你，可改用 [MCP Server](/usage/mcp) ——它的 `login`/`login_status` 工具在后台线程等待扫码，不会阻塞会话。
:::

## 认证文件

默认路径 `~/.config/mijia-api/auth.json`，可用 `-p /path/to/auth.json` 覆盖。全局参数的 `-p` 放在参数前；子命令（`get`/`set`/`action`/`statistics`/`run`）的 `-p` 放在子命令后。

## 典型工作流

以下流程均可由 LLM 自主完成（除登录外）：

1. **列出设备**，获取名称和 model：
   ```bash
   uvx mijiaAPI -l
   ```
2. **查看设备规格**（无需登录，发现可用的 `--prop_name` 和 `--action_name`）：
   ```bash
   uvx mijiaAPI --get_device_info yeelink.light.lamp4
   ```
3. **获取/设置属性**：
   ```bash
   uvx mijiaAPI get --dev_name "卧室台灯" --prop_name "brightness"
   uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "brightness" --value 60
   uvx mijiaAPI set --dev_name "卧室台灯" --prop_name "on" --value True
   ```
4. **执行设备动作**：
   ```bash
   uvx mijiaAPI action --dev_name "卧室台灯" --action_name toggle
   ```
5. **获取统计数据**：
   ```bash
   uvx mijiaAPI statistics --did 123456 --key 7.1 --data_type stat_month_v3
   ```

   统计接口仅支持部分设备，`key` 和 `data_type` 必须按型号确定。`7.1` 是
   `lumi.acpartner.mcn04` 的耗电量示例，`lumi.acpartner.mcn02` 则使用 `powerCost`；旧设备
   还可能使用不带 `_v3` 的统计类型。详见 [issue #46](https://github.com/Do1e/mijia-api/issues/46)
   和[米家统计接口文档](https://iot.mi.com/new/doc/accesses/direct-access/extension-development/extension-functions/statistical-interface)。

## 命令总览

| 命令 / 参数 | 用途 | 需要认证 | 阻塞 |
|-------------|------|----------|------|
| `login` | 二维码登录 | 否（创建认证） | 是（禁止调用） |
| `mcp` | 启动 MCP server（stdio） | 是 | 是（禁止调用） |
| `-l`、`--list_devices` | 列出所有设备（含共享） | 是 | 否 |
| `--list_homes` | 列出家庭、房间和设备 | 是 | 否 |
| `--list_scenes` | 列出各家庭场景 | 是 | 否 |
| `--list_consumable_items` | 列出各家庭耗材 | 是 | 否 |
| `--run_scene 名称/ID [...]` | 运行一个或多个场景 | 是 | 否 |
| `--get_device_info MODEL` | 按 model 获取设备规格 | 否 | 否 |
| `get` | 读取设备属性 | 是 | 否 |
| `set` | 设置设备属性 | 是 | 否 |
| `action` | 按动作名执行设备动作 | 是 | 否 |
| `statistics` | 获取设备统计数据 | 是 | 否 |
| `run` | 通过小爱音箱执行自然语言命令 | 是 | 否 |

::: tip
完整的命令行参数说明请参考 [CLI 参数参考](/reference/cli-args)，skill 的完整定义见仓库内的 [`skills/SKILL.md`](https://github.com/Do1e/mijia-api/blob/main/skills/SKILL.md)。
:::
