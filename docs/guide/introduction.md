# 项目简介

米家设备的 API，可以使用代码直接控制米家设备。

## 特性

- **扫码登录**：通过二维码登录米家账号，认证数据自动保存，Token 自动刷新
- **API 基础调用**：直接使用 siid/piid 获取/设置设备属性、执行设备动作
- **高级设备封装**：`mijiaDevice` 类提供面向对象的设备控制，无需关心 siid/piid
- **CLI 命令行工具**：直接在终端控制设备，支持 `uvx` 免安装运行
- **MCP Server**：让 LLM（如 Claude）直接控制米家设备
- **场景控制**：获取场景列表并执行手动场景
- **耗材管理**：获取耗材列表（如滤芯、灯泡等）
- **统计数据**：获取设备统计数据（如耗电量）
- **设备规格查询**：从[米家规格平台](https://home.miot-spec.com/)在线获取设备属性和动作信息

## 环境要求

- Python >= 3.10

## 链接

- [GitHub 仓库](https://github.com/Do1e/mijia-api)
- [PyPI 包](https://pypi.org/project/mijiaAPI/)
- [GPL-3.0 许可证](https://opensource.org/licenses/GPL-3.0)

## 致谢

- [janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)
- [米家 APP 网络请求的抓包、加解密与构造的代码笔记](https://imkero.net/posts/mihome-app-api/)
- [al-one/hass-xiaomi-miot](https://github.com/al-one/hass-xiaomi-miot)
