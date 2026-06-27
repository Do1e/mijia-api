# 更新日志

本文档记录了项目的 v1.3.7 以来的重要变更。

## [4.1.1](https://github.com/Do1e/mijia-api/compare/v4.1.0...v4.1.1) - 2026-06-27

### improvement

- CLI 的 `-l`/`--list_devices` 在列出设备时额外打印设备所属的 `家庭` 与 `房间`：通过家庭列表的 `roomlist` 反查每个设备 did 所在的家庭与房间，共享设备若不在任何房间则显示为"未知"；同时复用已获取的家庭列表，避免重复请求

## [4.1.0](https://github.com/Do1e/mijia-api/compare/v4.0.0...v4.1.0) - 2026-06-27

### new feature

- MCP server 新增 `login` 与 `login_status` 两个工具，支持在 MCP 会话内完成二维码登录，无需重启 server：`login` 先尝试刷新 token，失败则在后台线程长轮询等待扫码并返回二维码图片链接；`login_status` 查询登录结果（pending/success/error），成功后自动切换为新凭证
- MCP server 启动时不再因认证缺失/失效而立即退出，而是以未认证状态启动并提示调用 `login` 工具完成登录
- 新增 `skills/SKILL.md`，定义 mijia-api CLI 的 agent skill，供 AI 助手通过 `uvx mijiaAPI` 控制设备（明确禁止调用阻塞的 `login`/`mcp` 子命令）

### improvement

- MCP server 版本号与 Python 包版本同步，客户端可读取到正确的 server 版本
- 重构 `mijiaAPI` 的二维码登录流程，将原 `QRlogin` 拆分为 `_get_qr_login_data`（获取二维码数据，不阻塞）与 `_complete_qr_login`（长轮询完成登录）两个内部方法，供 MCP server 的 `login` 工具复用；公开的 `login()` / `QRlogin()` 行为不变
- CLI 的 `init_api` 在认证文件缺失、损坏或失效且刷新失败时，改为打印提示信息并以退出码 1 退出，提示用户运行 `mijiaAPI login`，不再自动触发登录（`login` 子命令本身仍执行登录）

## [4.0.0](https://github.com/Do1e/mijia-api/compare/v3.2.0...v4.0.0) - 2026-06-27

### new feature

- 新增基于 FastMCP 的 MCP 服务器（`mijiaAPI/mcp_server.py`），提供 11 个工具，覆盖家庭、设备、场景、属性、动作、统计与小爱音箱指令等全部主要 API
- CLI 新增 `mcp` 子命令，启动 MCP 服务器，启动时校验认证有效性，未认证时明确报错退出
- CLI 新增 `login` 子命令，用于通过 CLI 显式进行二维码登录

### improvement

- `requires-python` 提升至 `>=3.10`，新增 `fastmcp>=3.4.2` 依赖
- 精简 README，由 657 行缩减至约 50 行，仅保留项目简介、徽章、安装、最小快速上手示例与文档站点链接，详细用法迁移至 VitePress 文档站点
- 从仓库根目录移除 `CHANGELOG.md` 与 `FAQ.md`，内容已迁移至文档站点

## [3.2.0](https://github.com/Do1e/mijia-api/compare/v3.1.0...v3.2.0) - 2026-06-09

### improvement

- 将 `--run` 参数重构为独立的 `run` 子命令，提升 CLI 结构一致性
- 保留 `--run` 作为隐藏的废弃参数，并显示迁移提示

## [3.1.0](https://github.com/Do1e/mijia-api/compare/v3.0.5...v3.1.0) - 2026-05-27

### new feature

- 删除设备属性的 `unit` 属性，因为 home.miot-spec.com 上已废弃

### bugfix

- 适配 home.miot-spec.com 新的规格页格式
- 修复 execute-text-directive 中 quiet 参数的类型转换

## [3.0.5](https://github.com/Do1e/mijia-api/compare/v3.0.4...v3.0.5) - 2026-01-24

### bugfix

- 蓝牙设备控制返回 code 为 1 时表示网关已经接收指令，视为成功。

## [3.0.4](https://github.com/Do1e/mijia-api/compare/v3.0.3...v3.0.4) - 2026-01-12

### bugfix

- api 不可用时不对 `available` 进行缓存，以修复刷新 token 成功后依然提示不可用的问题

## [3.0.3](https://github.com/Do1e/mijia-api/compare/v3.0.2...v3.0.3) - 2026-01-02

### new feature

- 新增 `MIJIA_LOG_LEVEL` 环境变量支持，用于配置 CLI 日志级别

### bugfix

- 修复错误代码 "-10020" 描述中的错误拼写

## [3.0.2](https://github.com/Do1e/mijia-api/compare/v3.0.1...v3.0.2) - 2026-01-01

### new feature

- 为 `available` 属性添加了缓存机制，减少频繁调用带来的性能损耗

### chore

- 日志信息显示毫秒

## [3.0.1](https://github.com/Do1e/mijia-api/compare/v3.0.0...v3.0.1) - 2025-12-09

### new feature

- 新增 API `mijiaAPI.get_shared_devices_list()`，用于获取共享设备列表

### bugfix

- 修复了 alpine 下 `locale` 无法正常获取，默认使用 `zh_CN` 解决，如果需要在 alpine 下使用其他位置，请自行设置环境变量 `LC_ALL` 和 `LANG`。
- 修复了共享家庭中无权限的问题，确保传递正确的 `owner_id`。

## [3.0.0](https://github.com/Do1e/mijia-api/compare/v2.0.2...v3.0.0) - 2025-11-28

### new feature

- 使用最新的米家 API 接口，从 https://api.io.mi.com/app 切换到 https://api.mijia.tech/app
- `mijiaAPI` 类的初始化参数变更，请传递用于保存认证数据的路径 `auth_data_path` 而不是认证数据
- 彻底移除账号密码登录方式，仅支持二维码登录
- 部分 API 需要指定 `home_id`，不指定将遍历所有家庭
- 实现自动 `serviceToken` 刷新，现在理论上扫码一次能保活一个月
- 移除登录类 `mijiaLogin`，相关功能集成进入 `mijiaAPI` 类，请使用 `mijiaAPI.login()` / `mijiaAPI.QRlogin()`，两者均为二维码登录
- `mijiaDevice` 类的初始化参数变更，不再需要传递 `dev_info`，请选择传递 `did` 或 `dev_name` 进行初始化
- `mijiaDevice` 类的 `set`, `get`, `run_action` 彻底移除 `did` 参数，初始化时已完成
- 一些其他更改，请参考代码注释

## [2.0.2](https://github.com/Do1e/mijia-api/compare/v2.0.1...v2.0.2) - 2025-09-23

### bugfix

- 修复了 `set` 方法在类型检查前进行 value_list 检查，导致某些设备无法设置值的问题

## [2.0.1](https://github.com/Do1e/mijia-api/compare/v2.0.0...v2.0.1) - 2025-06-29

### bugfix

- 处理一个家庭中超过 200 个设备的情况，修复了 `get_devices_list` 方法可能无法获取所有设备的问题

### improvement

- 所有打印内容均使用中文

## [2.0.0](https://github.com/Do1e/mijia-api/compare/v1.5.0...v2.0.0) - 2025-06-27

#### 此版本有多项破坏性变更，请在升级后参考下述说明修复

### new feature

- 新增 API：`get_statistics`，用于获取设备的统计信息
- 新增文件 demos/decrypt.py 和 demos/decrypt_har.py，用于解密米家APP抓包
- `get_homes_list` 支持获取共享家庭
- `get_consumable_items` 支持获取共享家庭的耗材列表，需要额外指定 `owner_id` 参数
- `get_devices_list` 支持获取共享家庭的设备列表

### improvement

- 认证文件保存 `cUserId`，可作为 `userId` 的替代，暂时未使用
- **此版本彻底移除了 `mijiaDevices`，请及时替换为 `mijiaDevice`**
- **`mijiaDevice` 的 `set` 方法更换了参数顺序，请及时修复**
- **部分 API 调用后需要读取返回值的字典，如 `api.get_devices_list()['list']`，现在直接返回列表，请注意修改：**
  - `api.get_devices_list()['list']` -> `api.get_devices_list()`
  - `api.get_homes_list()['homelist']` -> `api.get_homes_list()`
  - `api.get_scenes_list(home_id)['scene_info_list']` -> `api.get_scenes_list(home_id)`
  - `api.get_consumable_items(home_id)['items']` -> `api.get_consumable_items(home_id)`

## [1.5.0](https://github.com/Do1e/mijia-api/compare/v1.4.5...v1.5.0) - 2025-06-19

### new feature

- 重命名 `mijiaDevices` 为 `mijiaDevice`

## [1.4.5](https://github.com/Do1e/mijia-api/compare/v1.4.4...v1.4.5) - 2025-06-16

### bugfix

- 登陆过程中无法获取用户信息时，处理相关报错

## [1.4.4](https://github.com/Do1e/mijia-api/compare/v1.4.3...v1.4.4) - 2025-06-14

### new feature

- `get_device_info` 支持 [https://home.miot-spec.com/](https://home.miot-spec.com/) 中的中文描述

### bugfix

- cli 修复了执行 `get_device_info` 必须先登录的问题

### improvement

- 优化日志输出
- 使用 `login` 方法的警告修改得更加明确

## [1.4.3](https://github.com/Do1e/mijia-api/compare/v1.4.2...v1.4.3) - 2025-05-22

### bugfix

- 针对部分特殊的设备，修复了 `get_device_info` 的 TypeError

## [1.4.2](https://github.com/Do1e/mijia-api/compare/v1.4.1...v1.4.2) - 2025-05-19

### new feature

- `get_device_info` 支持缓存结果以加速

## [1.4.1](https://github.com/Do1e/mijia-api/compare/v1.4.0...v1.4.1) - 2025-05-19

### new feature

- cli 支持 `--run` 以使用自然语言描述需求，交给小爱音箱执行

## [1.4.0](https://github.com/Do1e/mijia-api/compare/v1.3.14...v1.4.0) - 2025-05-19

### new feature

- 新增 `mijiaAPI` 的 cli 支持，运行 `mijiaAPI --help` 查看帮助

## [1.3.14](https://github.com/Do1e/mijia-api/compare/v1.3.13...v1.3.14) - 2025-05-18

### bugfix

- `available` 属性判断错误，始终返回 False

## [1.3.13](https://github.com/Do1e/mijia-api/compare/v1.3.12...v1.3.13) - 2025-05-18

### new feature

- 新增从 cookie 中提取有效期并保存在凭据中

### improvement

- `available` 属性根据有效期判断

## [1.3.12](https://github.com/Do1e/mijia-api/compare/v1.3.11...v1.3.12) - 2025-05-16

### improvement

- 简化 `mijiaLogin` 的初始化参数，根据 `save_path` 的值自动判断是否需要保存凭据
- 重构了对象初始化和方法的注释

## [1.3.11](https://github.com/Do1e/mijia-api/compare/v1.3.10...v1.3.11) - 2025-05-16

### bugfix

- 验证保存路径并确保在保存验证数据之前确保目录存在

## [1.3.10](https://github.com/Do1e/mijia-api/compare/v1.3.9...v1.3.10) - 2025-05-16

### improvement

- 使用 logging 模块替代 print 函数

## [1.3.9](https://github.com/Do1e/mijia-api/compare/v1.3.8...v1.3.9) - 2025-05-16

### new feature

- 新增用户个人信息查询
- 新增用户凭据的可选保存

### improvement

- 支持非 tty 的二维码打印
- 优化二维码图片的删除逻辑

## [1.3.8](https://github.com/Do1e/mijia-api/compare/v1.3.7...v1.3.8) - 2025-05-14

### improvement

- 新增了 devices 里所有方法的注释
- 新增了 `mijiaDevice` 实例化时的断言检查
- 新增了操作失败时的错误提示抛出与错误代码的详情
- 优化了 `mijiaDevice` 实例化时的内部变量的赋值逻辑
- 优化了多处代码的可读性与简洁性

### bugfix

- 修复多处由于数据类型更新而引发的警告

## [1.3.7](https://github.com/Do1e/mijia-api/compare/v1.3.6...v1.3.7) - 2025-05-14

### new feature

- 新增自定义 `run_action` 参数，`in` 等 python 关键字，可在前面加上下划线 `_`
- `mijiaDevice` 支持传入设备名称（米家中自定义的名称）进行初始化
