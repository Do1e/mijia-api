import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from .apis import mijiaAPI
from .devices import get_device_info, mijiaDevice
from .mcp_server import run as run_mcp
from .version import version


log_level_name = os.getenv('MIJIA_LOG_LEVEL', 'INFO').upper()
if log_level_name not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    raise ValueError(f"无效的日志级别: {log_level_name}, 可选值为 DEBUG, INFO, WARNING, ERROR, CRITICAL")
log_level = getattr(logging, log_level_name, logging.INFO)
logging.getLogger("mijiaAPI").setLevel(log_level)


def json_object(value: str) -> dict:
    try:
        result = json.loads(value)
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"无效 JSON: {e.msg}") from e
    if not isinstance(result, dict):
        raise argparse.ArgumentTypeError("必须是 JSON 对象")
    return result


def parse_args(args):
    parser = argparse.ArgumentParser(description=f"Mijia API CLI (v{version})")
    subparsers = parser.add_subparsers(dest='command')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"%(prog)s {version}",
        help="显示版本信息并退出",
    )
    parser.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    parser.add_argument(
        '--list_homes',
        action='store_true',
        help="列出家庭列表",
    )
    parser.add_argument(
        '-l', '--list_devices',
        action='store_true',
        help="列出所有米家设备，包含共享设备",
    )
    parser.add_argument(
        '--list_scenes',
        action='store_true',
        help="列出场景列表",
    )
    parser.add_argument(
        '--list_consumable_items',
        action='store_true',
        help="列出耗材列表",
    )
    parser.add_argument(
        '--run_scene',
        type=str,
        help="运行场景，指定场景ID或名称",
        nargs='+',
        metavar='SCENE_ID/SCENE_NAME',
    )
    parser.add_argument(
        '--get_device_info',
        type=str,
        help="获取设备信息，指定设备model，先使用 --list_devices 获取",
        metavar='DEVICE_MODEL',
    )
    parser.add_argument(
        '--run',
        type=str,
        help=argparse.SUPPRESS,
        nargs='?',
        default=None,
        metavar='PROMPT',
    )

    run = subparsers.add_parser(
        'run',
        help="使用自然语言描述你的需求，如果你有小爱音箱的话",
    )
    run.set_defaults(func='run')
    run.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    run.add_argument(
        'prompt',
        type=str,
        help="使用自然语言描述你的需求",
        metavar='PROMPT',
    )
    run.add_argument(
        '--wifispeaker_name',
        type=str,
        help="指定小爱音箱名称，默认是获取到的第一个小爱音箱",
        default=None,
    )
    run.add_argument(
        '--quiet',
        action='store_true',
        help="小爱音箱静默执行",
    )

    mcp_cmd = subparsers.add_parser(
        'mcp',
        help="启动 MCP server（stdio 传输）",
    )
    mcp_cmd.set_defaults(func='mcp')
    mcp_cmd.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )

    login_cmd = subparsers.add_parser(
        'login',
        help="二维码登录米家账号",
    )
    login_cmd.set_defaults(func='login')
    login_cmd.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )

    get = subparsers.add_parser(
        'get',
        help="获取设备属性",
    )
    get.set_defaults(func='get')
    get.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    get.add_argument(
        '--did',
        type=str,
        help="设备did，优先于 --dev_name 使用",
    )
    get.add_argument(
        '--dev_name',
        type=str,
        help="设备名称，指定为米家APP中设定的名称",
    )
    get.add_argument(
        '--prop_name',
        type=str,
        help="属性名称，先使用 --get_device_info 获取",
        required=True,
    )

    set = subparsers.add_parser(
        'set',
        help="设置设备属性",
    )
    set.set_defaults(func='set')
    set.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    set.add_argument(
        '--did',
        type=str,
        help="设备did，优先于 --dev_name 使用",
    )
    set.add_argument(
        '--dev_name',
        type=str,
        help="设备名称，指定为米家APP中设定的名称",
    )
    set.add_argument(
        '--prop_name',
        type=str,
        help="属性名称，先使用 --get_device_info 获取",
        required=True,
    )
    set.add_argument(
        '--value',
        type=str,
        help="需要设定的属性值",
        required=True,
    )

    action = subparsers.add_parser(
        'action',
        help="执行设备动作",
    )
    action.set_defaults(func='action')
    action.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    action_device = action.add_mutually_exclusive_group(required=True)
    action_device.add_argument(
        '--did',
        type=str,
        help="设备did",
    )
    action_device.add_argument(
        '--dev_name',
        type=str,
        help="设备名称，指定为米家APP中设定的名称",
    )
    action.add_argument(
        '--action_name',
        type=str,
        help="动作名称，先使用 --get_device_info 获取",
        required=True,
    )
    action.add_argument(
        '--params',
        type=json_object,
        help='动作参数 JSON 对象，例如 {"value":[2]}',
        default=None,
    )

    statistics = subparsers.add_parser(
        'statistics',
        help="获取设备统计数据",
    )
    statistics.set_defaults(func='statistics')
    statistics.add_argument(
        '-p', '--auth_path',
        type=Path,
        default=Path.home() / ".config" / "mijia-api" / "auth.json",
        help="认证文件保存路径，默认保存在 ~/.config/mijia-api/auth.json",
    )
    statistics.add_argument(
        '--did',
        type=str,
        help="设备did，先使用 --list_devices 获取",
        required=True,
    )
    statistics.add_argument(
        '--key',
        type=str,
        help='统计数据键，例如 "7.1"',
        required=True,
    )
    statistics.add_argument(
        '--data_type',
        type=str,
        help="统计类型，例如 stat_month_v3",
        required=True,
    )
    statistics.add_argument(
        '--limit',
        type=int,
        help="返回的最大条目数，默认 6",
        default=6,
    )
    statistics.add_argument(
        '--time_start',
        type=int,
        help="开始时间戳（秒），默认结束时间前 30 天",
    )
    statistics.add_argument(
        '--time_end',
        type=int,
        help="结束时间戳（秒），默认为当前时间",
    )
    return parser.parse_args(args)

def init_api(auth_path: Path) -> mijiaAPI:
    if Path(auth_path).is_dir():
        auth_path = auth_path / "auth.json"
    if not auth_path.exists():
        print(f"认证文件不存在: {auth_path}")
        print("请调用 'mijiaAPI login' 进行扫描登录")
        sys.exit(1)
    try:
        api = mijiaAPI(auth_data_path=auth_path)
    except json.JSONDecodeError:
        print(f"认证文件已损坏: {auth_path}")
        print("请调用 'mijiaAPI login' 进行扫描登录")
        sys.exit(1)
    if not api.available:
        try:
            api._refresh_token()
        except Exception:
            pass
        if not api.available:
            print(f"认证已失效且刷新失败: {auth_path}")
            print("请调用 'mijiaAPI login' 进行扫描登录")
            sys.exit(1)
    return api

def get_homes_list(api: mijiaAPI, verbose: bool = True, device_mapping: Optional[dict] = None) -> dict:
    if verbose:
        if device_mapping is None:
            device_mapping = get_devices_list(api, verbose=False)
    homes = api.get_homes_list()
    if verbose:
        print("家庭列表:")
        for home in homes:
            print(f"  - {home['name']}\n"
                  f"    ID: {home['id']}\n"
                  f"    地址: {home['address']}\n"
                  f"    房间数量: {len(home['roomlist'])}\n"
                  f"    创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(home['create_time']))}")
            print( "    房间列表:")
            for room in home['roomlist']:
                devices_name = []
                if room['dids']:
                    for did in room['dids']:
                        if did in device_mapping:
                            devices_name.append(device_mapping[did]['name'])
                        else:
                            devices_name.append(did)
                dids = ', '.join(devices_name)
                print(f"    - {room['name']}\n"
                      f"      ID: {room['id']}\n"
                      f"      设备列表: {dids}\n"
                      f"      创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(room['create_time']))}")
    home_mapping = {home['id']: home for home in homes}
    return home_mapping

def get_devices_list(api: mijiaAPI, verbose: bool = True, home_mapping: Optional[dict] = None) -> dict:
    devices = api.get_devices_list() + api.get_shared_devices_list()
    if verbose:
        if home_mapping is None:
            home_mapping = get_homes_list(api, verbose=False)
        did_location = {}
        for home in home_mapping.values():
            for room in home.get('roomlist', []):
                for did in room.get('dids', []) or []:
                    did_location[did] = (home['name'], room['name'])
        print("设备列表:")
        for device in devices:
            home_name, room_name = did_location.get(device['did'], ("未知", "未知"))
            print(f"  - {device['name']}\n"
                    f"    did: {device['did']}\n"
                    f"    model: {device['model']}\n"
                    f"    home: {home_name}\n"
                    f"    room: {room_name}\n"
                    f"    online: {device['isOnline']}")
    device_mapping = {device['did']: device for device in devices}
    return device_mapping

def get_scenes_list(api: mijiaAPI, verbose: bool = True, home_mapping: Optional[dict] = None) -> dict:
    if home_mapping is None:
        home_mapping = get_homes_list(api, verbose=False)
    scene_mapping = {}
    for home_id, home in home_mapping.items():
        scenes = api.get_scenes_list(home_id)
        if scenes and verbose:
            print(f"{home['name']} ({home_id}) 中的场景:")
            for scene in scenes:
                print(f"  - {scene['name']}\n"
                      f"    ID: {scene['scene_id']}\n"
                      f"    创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(scene['create_time'])))}\n")
        scene_mapping.update({scene['scene_id']: scene for scene in scenes})
    return scene_mapping

def get_consumable_items(api: mijiaAPI, home_mapping: Optional[dict] = None):
    if home_mapping is None:
        home_mapping = get_homes_list(api, verbose=False)
    for home_id, home in home_mapping.items():
        items = api.get_consumable_items(home_id)
        print(f"{home['name']} ({home_id}) 中的耗材:")
        for item in items:
            print(f"  - {item['name']}({item['did']}) 中的 {item['details']['description']}\n"
                  f"    值: {item['details']['value']}")

def run_scene(api: mijiaAPI, scene_id: str, scene_mapping: Optional[dict] = None) -> bool:
    if scene_mapping is None:
        scene_mapping = get_scenes_list(api, verbose=False)
    if scene_id not in scene_mapping:
        scene_name_to_find = scene_id
        found = False
        for sid, scene in scene_mapping.items():
            if scene['name'] == scene_name_to_find:
                scene_id = sid
                found = True
                break
        if not found:
            print(f"场景 {scene_name_to_find} 未找到")
            return False
    scene_name = scene_mapping[scene_id]['name']
    scence_home_id = scene_mapping[scene_id]['home_id']
    ret = api.run_scene(scene_id, scence_home_id)
    if ret:
        print(f"场景 {scene_name}({scene_id}) 运行成功")
        return True
    else:
        print(f"运行场景 {scene_name}({scene_id}) 失败")
        return False

def get(args):
    api = init_api(args.auth_path)
    device = mijiaDevice(api, did=args.did, dev_name=args.dev_name)
    value = device.get(args.prop_name)
    print(f"{device.name} ({device.did}) 的 {args.prop_name} 值为 {value}")

def set(args):
    api = init_api(args.auth_path)
    device = mijiaDevice(api, did=args.did, dev_name=args.dev_name)
    try:
        device.set(args.prop_name, args.value)
    except Exception as e:
        print(f"设置 {args.dev_name} 的 {args.prop_name} 值为 {args.value} 失败: {e}")
        return
    print(f"{device.name} ({device.did}) 的 {args.prop_name} 值已设置为 {args.value}")


def run_action(api: mijiaAPI, args):
    device = mijiaDevice(api, did=args.did, dev_name=args.dev_name)
    device.run_action(args.action_name, **(args.params or {}))
    print(f"{device.name} ({device.did}) 的动作 {args.action_name} 指令已发送")


def get_statistics(api: mijiaAPI, args):
    time_end = args.time_end if args.time_end is not None else int(time.time())
    time_start = args.time_start if args.time_start is not None else time_end - 30 * 24 * 3600
    result = api.get_statistics({
        "did": args.did,
        "key": args.key,
        "data_type": args.data_type,
        "limit": args.limit,
        "time_start": time_start,
        "time_end": time_end,
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main(args):
    args = parse_args(args)

    if args.run is not None:
        print("错误: '--run' 参数已弃用，请使用 'run' 子命令代替。")
        print(f"新用法: mijiaAPI run \"{args.run}\"")
        sys.exit(1)

    if args.get_device_info:
        device_info = get_device_info(args.get_device_info)
        print(json.dumps(device_info, indent=2, ensure_ascii=False))
    if not (args.list_devices or
            args.list_homes or
            args.list_scenes or
            args.list_consumable_items or
            args.run_scene or
            hasattr(args, 'func') and args.func is not None):
        return

    if hasattr(args, 'func') and args.func == 'mcp':
        run_mcp(args.auth_path)
        return
    if hasattr(args, 'func') and args.func == 'login':
        auth_path = args.auth_path
        file_path = Path(auth_path) / "auth.json" if Path(auth_path).is_dir() else Path(auth_path)
        try:
            api = mijiaAPI(auth_data_path=auth_path)
        except json.JSONDecodeError:
            file_path.unlink(missing_ok=True)
            api = mijiaAPI(auth_data_path=auth_path)
        if not api.available:
            api.login()
        return

    api = init_api(args.auth_path)
    device_mapping = None
    home_mapping = None
    scenes_mapping = None

    if args.list_devices:
        if home_mapping is None:
            home_mapping = get_homes_list(api, verbose=False)
        device_mapping = get_devices_list(api, home_mapping=home_mapping)
    if args.list_homes:
        home_mapping = get_homes_list(api, device_mapping=device_mapping)
    if args.list_scenes:
        scenes_mapping = get_scenes_list(api, home_mapping=home_mapping)
    if args.list_consumable_items:
        get_consumable_items(api, home_mapping=home_mapping)
    if args.run_scene:
        for scene_id in args.run_scene:
            run_scene(api, scene_id, scene_mapping=scenes_mapping)
    if hasattr(args, 'func') and args.func is not None:
        if args.func == 'get':
            get(args)
        if args.func == 'set':
            set(args)
        if args.func == 'action':
            run_action(api, args)
        if args.func == 'statistics':
            get_statistics(api, args)
        if args.func == 'run':
            if device_mapping is None:
                device_mapping = get_devices_list(api, verbose=False)
            if args.wifispeaker_name is None:
                wifispeaker = None
                for device in device_mapping.values():
                    if 'xiaomi.wifispeaker' in device['model']:
                        wifispeaker = mijiaDevice(api, dev_name=device['name'])
                        break
                if wifispeaker is None:
                    raise ValueError("未找到小爱音箱设备")
            else:
                wifispeaker = mijiaDevice(api, dev_name=args.wifispeaker_name)
            wifispeaker.run_action('execute-text-directive', _in=[args.prompt, 1 if args.quiet else 0])

def cli():
    main(sys.argv[1:])

if __name__ == "__main__":
    main(sys.argv[1:])
