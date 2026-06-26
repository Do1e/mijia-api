import json
import logging
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .apis import mijiaAPI
from .devices import get_device_info, mijiaDevice
from .errors import LoginError
from .logger import logger


mcp = FastMCP("mijia-api")

_api: Optional[mijiaAPI] = None
_auth_path: Optional[Path] = None


def _get_api() -> mijiaAPI:
    global _api
    if _api is not None:
        return _api
    raise RuntimeError("mijiaAPI 未初始化，请先登录后重启 MCP server")


def _refresh_if_needed(api: mijiaAPI) -> None:
    if not api.available:
        try:
            api._refresh_token()
        except LoginError:
            raise RuntimeError(
                "认证已失效且无法自动刷新，请运行 "
                f"`mijiaAPI login -p {_auth_path}` 重新登录后重启 MCP server"
            )


def run(auth_path: Path) -> None:
    global _api, _auth_path
    _auth_path = auth_path if not auth_path.is_dir() else auth_path / "auth.json"

    if not _auth_path.exists():
        print(
            f"认证文件不存在: {_auth_path}\n"
            f"请先运行 `mijiaAPI login -p {_auth_path}` 登录后再启动 MCP server",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler) or h.stream is sys.stderr]
    try:
        _api = mijiaAPI(auth_data_path=_auth_path)
        if not _api.available:
            _api._refresh_token()
        if not _api.available:
            raise LoginError(-1, "认证不可用")
    except Exception as e:
        print(
            f"认证不可用且无法自动刷新: {e}\n"
            f"请运行 `mijiaAPI login -p {_auth_path}` 重新登录后再启动 MCP server",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info(f"MCP server 启动，认证文件: {_auth_path}")
    mcp.run()


@mcp.tool
def list_homes() -> str:
    """列出米家所有家庭及房间信息。

    返回每个家庭的名称、ID、地址、房间列表（含房间内设备名称）。
    """
    api = _get_api()
    _refresh_if_needed(api)
    homes = api.get_homes_list()
    return json.dumps(homes, ensure_ascii=False)


@mcp.tool
def list_devices(home_id: Optional[str] = None) -> str:
    """列出米家设备列表（包含共享设备）。

    参数:
        home_id: 可选，指定家庭ID则仅列出该家庭的设备；不传则列出所有设备。

    返回每个设备的名称、did、model、在线状态等。
    """
    api = _get_api()
    _refresh_if_needed(api)
    devices = api.get_devices_list() + api.get_shared_devices_list()
    if home_id is not None:
        devices = [d for d in devices if d.get("home_id") == home_id]
    return json.dumps(devices, ensure_ascii=False)


@mcp.tool
def list_scenes(home_id: Optional[str] = None) -> str:
    """列出米家手动场景列表。

    参数:
        home_id: 可选，指定家庭ID则仅列出该家庭的场景；不传则列出所有场景。

    返回每个场景的名称、scene_id、所属家庭等。
    """
    api = _get_api()
    _refresh_if_needed(api)
    scenes = api.get_scenes_list(home_id)
    return json.dumps(scenes, ensure_ascii=False)


@mcp.tool
def list_consumables(home_id: Optional[str] = None) -> str:
    """列出耗材列表（如滤芯、电池等需更换的配件）。

    参数:
        home_id: 可选，指定家庭ID则仅列出该家庭的耗材；不传则列出所有耗材。

    返回耗材所属设备、描述、当前值等。
    """
    api = _get_api()
    _refresh_if_needed(api)
    items = api.get_consumable_items(home_id)
    return json.dumps(items, ensure_ascii=False)


@mcp.tool
def get_device_spec(device_model: str) -> str:
    """获取设备规格信息（属性和动作列表）。

    参数:
        device_model: 设备型号，例如 'yeelink.light.lamp4'，可从 list_devices 获取。

    返回设备支持的属性（名称/描述/类型/读写/范围/枚举值）和动作列表，
    用于确定 get_device_properties / set_device_property / run_device_action 的可用参数名。
    """
    api = _get_api()
    info = get_device_info(device_model, cache_path=api.auth_data_path.parent)
    return json.dumps(info, ensure_ascii=False)


@mcp.tool
def get_device_properties(
    dev_name: Optional[str] = None,
    did: Optional[str] = None,
    prop_names: Optional[list[str]] = None,
) -> str:
    """获取设备属性值（高层封装，无需 siid/piid）。

    参数:
        dev_name: 设备名称（米家APP中设定），与 did 二选一。
        did: 设备did，优先于 dev_name。
        prop_names: 属性名列表（如 ["brightness", "on"]），可从 get_device_spec 获取；
                    不传则返回设备所有可读属性的值。

    返回属性名与对应值的映射。
    """
    api = _get_api()
    _refresh_if_needed(api)
    device = mijiaDevice(api, did=did, dev_name=dev_name)
    names = prop_names if prop_names else [k for k in device.prop_list if "_" not in k]
    result = {}
    for name in names:
        prop = device.prop_list.get(name)
        if prop is None or "r" not in prop.rw:
            continue
        try:
            result[name] = device.get(name)
        except Exception as e:
            result[name] = f"<读取失败: {e}>"
    return json.dumps(result, ensure_ascii=False)


@mcp.tool
def set_device_property(
    prop_name: str,
    value: str,
    dev_name: Optional[str] = None,
    did: Optional[str] = None,
) -> str:
    """设置设备属性值（高层封装，无需 siid/piid）。

    参数:
        prop_name: 属性名，可从 get_device_spec 获取。
        value: 要设置的值。布尔值传 "true"/"false"；数值传对应数字字符串。
        dev_name: 设备名称（米家APP中设定），与 did 二选一。
        did: 设备did，优先于 dev_name。

    返回设置结果。
    """
    api = _get_api()
    _refresh_if_needed(api)
    device = mijiaDevice(api, did=did, dev_name=dev_name)
    device.set(prop_name, value)
    return f"{device.name}({device.did}) 的 {prop_name} 已设置为 {value}"


@mcp.tool
def run_device_action(
    action_name: str,
    dev_name: Optional[str] = None,
    did: Optional[str] = None,
    value: Optional[list] = None,
) -> str:
    """执行设备动作（高层封装，无需 siid/aiid）。

    参数:
        action_name: 动作名，可从 get_device_spec 获取。
        dev_name: 设备名称（米家APP中设定），与 did 二选一。
        did: 设备did，优先于 dev_name。
        value: 可选，动作参数列表，根据具体动作定义而定。

    返回执行结果。
    """
    api = _get_api()
    _refresh_if_needed(api)
    device = mijiaDevice(api, did=did, dev_name=dev_name)
    device.run_action(action_name, value=value)
    return f"{device.name}({device.did}) 的动作 {action_name} 执行成功"


@mcp.tool
def run_scene(scene_id_or_name: str) -> str:
    """运行米家手动场景。

    参数:
        scene_id_or_name: 场景ID或场景名称。名称需唯一，否则请使用 scene_id。

    返回执行结果。
    """
    api = _get_api()
    _refresh_if_needed(api)
    scenes = api.get_scenes_list()
    scene_mapping = {s["scene_id"]: s for s in scenes}
    target = scene_id_or_name
    if target not in scene_mapping:
        found = [s for s in scenes if s["name"] == target]
        if not found:
            return f"场景 {scene_id_or_name} 未找到"
        if len(found) > 1:
            return f"找到多个名为 {scene_id_or_name} 的场景，请使用 scene_id"
        target = found[0]["scene_id"]
    scene = scene_mapping[target]
    ret = api.run_scene(target, scene["home_id"])
    return f"场景 {scene['name']}({target}) 运行{'成功' if ret else '失败'}"


@mcp.tool
def get_statistics(
    did: str,
    key: str,
    data_type: str,
    limit: int = 6,
    time_start: Optional[int] = None,
    time_end: Optional[int] = None,
) -> str:
    """获取设备统计数据（如耗电量、使用时长）。

    参数:
        did: 设备ID，可从 list_devices 获取。
        key: 统计数据键，格式为 siid.piid（如 "7.1"），需根据设备型号确定。
        data_type: 统计粒度，可选 stat_hour_v3 / stat_day_v3 / stat_week_v3 / stat_month_v3。
        limit: 返回最大条目数，默认6。
        time_start: 起始时间戳（秒），不传默认为30天前。
        time_end: 结束时间戳（秒），不传默认为当前时间。

    返回统计条目列表（时间戳与数值）。
    """
    import time
    api = _get_api()
    _refresh_if_needed(api)
    now = int(time.time())
    data = {
        "did": did,
        "key": key,
        "data_type": data_type,
        "limit": limit,
        "time_start": time_start if time_start is not None else now - 30 * 24 * 3600,
        "time_end": time_end if time_end is not None else now,
    }
    ret = api.get_statistics(data)
    return json.dumps(ret, ensure_ascii=False)


@mcp.tool
def run_speaker_command(
    prompt: str,
    speaker_name: Optional[str] = None,
    quiet: bool = False,
) -> str:
    """通过小爱音箱执行自然语言指令。

    参数:
        prompt: 自然语言指令，如 "打开卧室台灯"、"把亮度调到50%"。
        speaker_name: 可选，指定小爱音箱名称，默认使用获取到的第一个小爱音箱。
        quiet: 是否静默执行（不语音播报），默认 False。

    返回执行结果。
    """
    api = _get_api()
    _refresh_if_needed(api)
    devices = api.get_devices_list()
    if speaker_name is None:
        match = None
        for device in devices:
            if "xiaomi.wifispeaker" in device["model"]:
                match = device
                break
        if match is None:
            return "未找到小爱音箱设备"
    else:
        matches = [d for d in devices if d["name"] == speaker_name]
        if not matches:
            return f"未找到名为 {speaker_name} 的小爱音箱"
        match = matches[0]
    speaker = mijiaDevice(api, did=match["did"])
    speaker.run_action("execute-text-directive", _in=[prompt, 1 if quiet else 0])
    return f"已通过 {match['name']} 执行: {prompt}"
