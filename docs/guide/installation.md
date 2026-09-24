# 安装

> 要求 Python >= 3.10

## 从 PyPI 安装（推荐）

```bash
pip install mijiaAPI
# uv 用户可使用 `uv add mijiaAPI`
```

## 可选依赖

MCP Server 功能依赖 `fastmcp`，该依赖不随主包安装，需通过 `mcp` extra 安装：

```bash
pip install "mijiaAPI[mcp]"
# uv 用户可使用 `uv add "mijiaAPI[mcp]"`
```

未安装时仅有 `mijiaAPI mcp` 子命令不可用（会提示缺少依赖并退出），Python API 与其他 CLI 子命令不受影响。

## 从源码安装

```bash
git clone https://github.com/Do1e/mijia-api.git
cd mijia-api
pip install .
# 或 `pip install -e .` 以可编辑模式安装
# 或 `pip install ".[mcp]"` 一并安装 MCP server 依赖
# 或 `pip install git+https://github.com/Do1e/mijia-api.git` 直接从仓库安装
# uv 用户可使用 `uv add git+https://github.com/Do1e/mijia-api.git`
```

## AUR（Arch User Repository）

如果你使用 Arch Linux 或基于 Arch 的发行版，可以通过 AUR 安装：

```bash
yay -S python-mijia-api
```
