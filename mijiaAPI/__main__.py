import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from .apis import mijiaAPI
from .devices import get_device_info, mijiaDevice
from .version import version


logging.getLogger("mijiaAPI").setLevel(logging.INFO)

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
        help="使用自然语言描述你的需求，如果你有小爱音箱的话",
        metavar='PROMPT',
    )
    parser.add_argument(
        '--wifispeaker_name',
        type=str,
        help="指定小爱音箱名称，默认是获取到的第一个小爱音箱",
        default=None,
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="小爱音箱静默执行",
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
    return parser.parse_args(args)

def init_api(auth_path: Path) -> mijiaAPI:
    class APIUnavailableError(Exception):
        pass

    if Path(auth_path).is_dir():
        auth_path = auth_path / "auth.json"
    if auth_path.exists():
        try:
            api = mijiaAPI(auth_data_path=auth_path)
            if not api.available:
                api._refresh_token()
            if not api.available:
                raise APIUnavailableError()
            return api
        except (json.JSONDecodeError, APIUnavailableError):
            auth_path.unlink(missing_ok=True)
            api = mijiaAPI(auth_data_path=auth_path)
            api.login()
    else:
        api = mijiaAPI(auth_data_path=auth_path)
        api.login()
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

def get_devices_list(api: mijiaAPI, verbose: bool = True) -> dict:
    devices = api.get_devices_list() + api.get_shared_devices_list()
    if verbose:
        print("设备列表:")
        for device in devices:
            print(f"  - {device['name']}\n"
                    f"    did: {device['did']}\n"
                    f"    model: {device['model']}\n"
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
    unit = device.prop_list[args.prop_name].unit
    print(f"{device.name} ({device.did}) 的 {args.prop_name} 值为 {value} {unit if unit else ''}")

def set(args):
    api = init_api(args.auth_path)
    device = mijiaDevice(api, did=args.did, dev_name=args.dev_name)
    try:
        device.set(args.prop_name, args.value)
    except Exception as e:
        print(f"设置 {args.dev_name} 的 {args.prop_name} 值为 {args.value} 失败: {e}")
        return
    unit = device.prop_list[args.prop_name].unit
    print(f"{device.name} ({device.did}) 的 {args.prop_name} 值已设置为 {args.value} {unit if unit else ''}")

def main(args):
    args = parse_args(args)

    if args.get_device_info:
        device_info = get_device_info(args.get_device_info)
        print(json.dumps(device_info, indent=2, ensure_ascii=False))
    if not (args.list_devices or
            args.list_homes or
            args.list_scenes or
            args.list_consumable_items or
            args.run_scene or
            args.run or
            hasattr(args, 'func') and args.func is not None):
        return

    api = init_api(args.auth_path)
    device_mapping = None
    home_mapping = None
    scenes_mapping = None

    if args.list_devices:
        device_mapping = get_devices_list(api)
    if args.list_homes:
        home_mapping = get_homes_list(api, device_mapping=device_mapping)
    if args.list_scenes:
        scenes_mapping = get_scenes_list(api, home_mapping=home_mapping)
    if args.list_consumable_items:
        get_consumable_items(api, home_mapping=home_mapping)
    if args.run_scene:
        for scene_id in args.run_scene:
            run_scene(api, scene_id, scene_mapping=scenes_mapping)
    if args.run:
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
        wifispeaker.run_action('execute-text-directive', _in=[args.run, args.quiet])
    if hasattr(args, 'func') and args.func is not None:
        if args.func == 'get':
            get(args)
        if args.func == 'set':
            set(args)

def cli():
    main(sys.argv[1:])

if __name__ == "__main__":
    main(sys.argv[1:])
