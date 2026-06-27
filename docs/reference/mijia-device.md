# mijiaDevice 类

`mijiaDevice` 类提供高级封装，让您可以像操作普通对象一样控制设备，无需关心 siid/piid。

## 构造函数

```python
mijiaDevice(
    api: mijiaAPI,
    did: Optional[str] = None,
    dev_name: Optional[str] = None,
    sleep_time: float = 0.5
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api` | `mijiaAPI` | （必填） | 已登录的 `mijiaAPI` 实例 |
| `did` | `Optional[str]` | `None` | 设备 ID。与 `dev_name` 二选一，同时给出时优先使用 |
| `dev_name` | `Optional[str]` | `None` | 设备名称（米家 APP 中设定的名称）。名称必须唯一，否则抛出 `MultipleDevicesFoundError` |
| `sleep_time` | `float` | `0.5` | 每次操作后的休眠时间（秒），避免请求过快 |

::: tip
`did` 与 `dev_name` 至少提供一个，否则抛出 `ValueError("必须提供 did 或 dev_name 参数之一")`。
:::

## 方法

### get

```python
get(name: str) -> Union[bool, int, float, str]
```

获取设备属性值。

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 属性名称 |

### set

```python
set(name: str, value: Union[bool, int, float, str])
```

设置设备属性值。无返回值。

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 属性名称 |
| `value` | `Union[bool, int, float, str]` | 属性值 |

### run_action

```python
run_action(name: str, value: Optional[Union[list, tuple]] = None, **kwargs)
```

执行设备动作。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | （必填） | 动作名称 |
| `value` | `Optional[Union[list, tuple]]` | `None` | 动作参数 |

### \_\_str\_\_

```python
__str__() -> str
```

返回设备名称、型号及所有支持的属性和动作概览。

## 属性访问代理

`mijiaDevice` 通过 `__getattr__` 和 `__setattr__` 实现了属性值的直接读写：

```python
# 读取属性（等同于 device.get('brightness')）
brightness = device.brightness

# 写入属性（等同于 device.set('brightness', 60)）
device.brightness = 60
```

::: tip
包含 `-` 的属性名请使用下划线 `_` 替代，例如 `color-temperature` 对应 `device.color_temperature`。
Python 关键字（如 `in`）可在前面加上下划线 `_`，如 `device._in`。
:::

## 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `prop_list` | `dict` | 所有支持的属性，键为属性名，值为 `DevProp` 对象 |
| `action_list` | `dict` | 所有支持的动作，键为动作名，值为 `DevAction` 对象 |

### DevProp 对象

| 属性 | 说明 |
|------|------|
| `desc` | 属性描述 |
| `type` | 属性类型 |
| `rw` | 读写权限 |

### DevAction 对象

| 属性 | 说明 |
|------|------|
| `desc` | 动作描述 |

## get_device_info 函数

```python
get_device_info(
    device_model: str,
    cache_path: Optional[Union[str, Path]] = None
) -> dict
```

从[米家规格平台](https://home.miot-spec.com/)在线获取设备规格信息，支持缓存。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `device_model` | `str` | （必填） | 设备型号，如 `yeelink.light.lamp4` |
| `cache_path` | `Optional[Union[str, Path]]` | `None` | 缓存路径，指定后会缓存结果以加速 |
