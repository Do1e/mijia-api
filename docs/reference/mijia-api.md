# mijiaAPI 类

`mijiaAPI` 类是米家 API 的核心类，负责认证、登录和所有 API 调用。

## 构造函数

```python
mijiaAPI(auth_data_path: Optional[str] = None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `auth_data_path` | `Optional[str]` | `None` | 认证文件保存路径。默认为 `~/.config/mijia-api/auth.json` |

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `available` | `bool` | 判断 Token 是否有效（带 60 秒缓存） |
| `pass_o` | `str` | — |
| `user_agent` | `str` | — |
| `deviceId` | `str` | — |

## 方法

### login

```python
login(*args, **kwargs) -> dict
```

二维码登录方法（内部调用 `QRlogin`）。如果 Token 有效会自动跳过。

### QRlogin

```python
QRlogin() -> dict
```

二维码登录方法。登录时会在终端打印二维码，使用米家APP扫描完成身份验证。

### check_new_msg

```python
check_new_msg(
    begin_at: int = int(time.time()) - 3600,
    refresh_token: bool = True
) -> dict
```

检查新消息，同时可用于刷新 Token。

### get_homes_list

```python
get_homes_list() -> list
```

获取用户的所有家庭列表（包含共享家庭）。

### get_devices_list

```python
get_devices_list(home_id: Optional[str] = None) -> list
```

获取设备列表。不指定 `home_id` 时遍历所有家庭。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `home_id` | `Optional[str]` | `None` | 家庭 ID，不指定则获取所有家庭的设备 |

### get_shared_devices_list

```python
get_shared_devices_list() -> list
```

获取共享设备列表（无法指定家庭 ID）。

### get_scenes_list

```python
get_scenes_list(home_id: Optional[str] = None) -> list
```

获取场景列表。不指定 `home_id` 时遍历所有家庭。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `home_id` | `Optional[str]` | `None` | 家庭 ID |

### run_scene

```python
run_scene(scene_id: str, home_id: str) -> bool
```

执行手动场景。

| 参数 | 类型 | 说明 |
|------|------|------|
| `scene_id` | `str` | 场景 ID |
| `home_id` | `str` | 家庭 ID |

### get_consumable_items

```python
get_consumable_items(home_id: Optional[str] = None) -> list
```

获取耗材列表（如滤芯、灯泡等）。不指定 `home_id` 时遍历所有家庭。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `home_id` | `Optional[str]` | `None` | 家庭 ID |

### get_devices_prop

```python
get_devices_prop(data: Union[list, dict]) -> Union[list, dict]
```

获取设备属性（原始 siid/piid 方式）。支持单个（dict）和批量（list）操作。

### set_devices_prop

```python
set_devices_prop(data: Union[list, dict]) -> Union[list, dict]
```

设置设备属性（原始 siid/piid 方式）。支持单个（dict）和批量（list）操作。

### run_action

```python
run_action(data: Union[list, dict]) -> Union[list, dict]
```

执行设备操作（原始 siid/aiid 方式）。支持单个（dict）和批量（list）操作。

### get_statistics

```python
get_statistics(data: dict) -> list
```

获取设备统计数据（如耗电量）。

`data` 参数字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `did` | `str` | 设备 ID |
| `key` | `str` | 属性键，格式为 `siid.piid`，如 `"7.1"` |
| `data_type` | `str` | 统计类型：`stat_hour_v3`, `stat_day_v3`, `stat_week_v3`, `stat_month_v3` |
| `limit` | `int` | 返回的最大条目数 |
| `time_start` | `int` | 开始时间戳（秒） |
| `time_end` | `int` | 结束时间戳（秒） |
