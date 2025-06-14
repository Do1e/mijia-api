from typing import Optional
import argparse
import json
import os
import sys
import time

from .apis import mijiaAPI
from .devices import mijiaDevices, get_device_info
from .login import mijiaLogin

def parse_args(args):
    parser = argparse.ArgumentParser(description="Mijia API CLI")
    subparsers = parser.add_subparsers(dest='command')
    parser.add_argument(
        '-p', '--auth_path',
        type=str,
        default=os.path.join(os.path.expanduser("~"), ".config/mijia-api", "mijia-api-auth.json"),
        help="认证文件保存路径，默认保存在~/.config/mijia-api/mijia-api-auth.json",
    )
    parser.add_argument(
        '-l', '--list_devices',
        action='store_true',
        help="列出所有米家设备",
    )
    parser.add_argument(
        '--list_homes',
        action='store_true',
        help="列出家庭列表",
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
        type=str,
        default=os.path.join(os.path.expanduser("~"), ".config/mijia-api", "mijia-api-auth.json"),
        help="认证文件保存路径，默认保存在~/.config/mijia-api/mijia-api-auth.json",
    )
    get.add_argument(
        '--dev_name',
        type=str,
        help="设备名称，指定为米家APP中设定的名称",
        required=True,
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
        type=str,
        default=os.path.join(os.path.expanduser("~"), ".config/mijia-api", "mijia-api-auth.json"),
        help="认证文件保存路径，默认保存在~/.config/mijia-api/mijia-api-auth.json",
    )
    set.add_argument(
        '--dev_name',
        type=str,
        help="设备名称，指定为米家APP中设定的名称",
        required=True,
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

def init_api(auth_path: str) -> mijiaAPI:
    if os.path.isdir(auth_path):
        auth_path = os.path.join(auth_path, "mijia-api-auth.json")
    if os.path.exists(auth_path):
        try:
            with open(auth_path, 'r') as f:
                auth = json.load(f)
            api = mijiaAPI(auth_data=auth)
            if not api.available:
                raise ValueError("Saved auth is no longer valid")
        except (json.JSONDecodeError, ValueError):
            api = mijiaLogin(save_path=auth_path)
            auth = api.QRlogin()
            api = mijiaAPI(auth_data=auth)
    else:
        api = mijiaLogin(save_path=auth_path)
        auth = api.QRlogin()
        api = mijiaAPI(auth_data=auth)
    return api

def get_devices_list(api: mijiaAPI, verbose: bool = True) -> dict:
    devices = api.get_devices_list()
    if 'list' in devices:
        devices = devices['list']
    else:
        devices = []
    if verbose:
        print("Devices:")
        for device in devices:
            print(f"  - {device['name']}\n"
                    f"    did: {device['did']}\n"
                    f"    model: {device['model']}\n"
                    f"    online: {device['isOnline']}")
    device_mapping = {device['did']: device for device in devices}
    return device_mapping

def get_homes_list(api: mijiaAPI, verbose: bool = True, device_mapping: Optional[dict] = None) -> dict:
    if verbose:
        if device_mapping is None:
            device_mapping = get_devices_list(api, verbose=False)
    homes = api.get_homes_list()
    if 'homelist' in homes:
        homes = homes['homelist']
    else:
        homes = []
    if verbose:
        print("Homes:")
        for home in homes:
            print(f"  - {home['name']}\n"
                f"    id: {home['id']}\n"
                f"    address: {home['address']}\n"
                f"    room count: {len(home['roomlist'])}\n"
                f"    create time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(home['create_time']))}")
            print("    Rooms:")
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
                      f"      id: {room['id']}\n"
                      f"      dids: {dids}\n"
                      f"      create time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(room['create_time']))}")
    home_mapping = {home['id']: home for home in homes}
    return home_mapping

def get_scenes_list(api: mijiaAPI, verbose: bool = True, home_mapping: Optional[dict] = None) -> dict:
    if home_mapping is None:
        home_mapping = get_homes_list(api, verbose=False)
    scene_mapping = {}
    for home_id, home in home_mapping.items():
        scenes = api.get_scenes_list(home_id)
        if 'scene_info_list' in scenes:
            scenes = scenes['scene_info_list']
        else:
            scenes = []
        if scenes and verbose:
            print(f"Scenes in {home['name']} ({home_id}):")
            for scene in scenes:
                print(f"  - {scene['name']}\n"
                      f"    id: {scene['scene_id']}\n"
                      f"    create time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(scene['create_time'])))}\n"
                      f"    update time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(scene['update_time'])))}")
        scene_mapping.update({scene['scene_id']: scene for scene in scenes})
    return scene_mapping

def get_consumable_items(api: mijiaAPI, home_mapping: Optional[dict] = None):
    if home_mapping is None:
        home_mapping = get_homes_list(api, verbose=False)
    for home_id, home in home_mapping.items():
        items = api.get_consumable_items(home_id)
        if 'items' in items:
            items = items['items'][0]['consumes_data']
        else:
            items = []
        print(f"Consumable items in {home['name']} ({home_id}):")
        for item in items:
            print(f"  - {item['details'][0]['description']} in {item['name']}({item['did']})\n"
                  f"    value: {item['details'][0]['value']}")

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
            print(f"Scene {scene_name_to_find} not found")
            return False
    scene_name = scene_mapping[scene_id]['name']
    ret = api.run_scene(scene_id)
    if ret:
        print(f"Scene {scene_name}({scene_id}) run successfully")
        return True
    else:
        print(f"Failed to run scene {scene_name}({scene_id})")
        return False

def get(args):
    api = init_api(args.auth_path)
    device = mijiaDevices(api, dev_name=args.dev_name)
    value = device.get(args.prop_name)
    unit = device.prop_list[args.prop_name].unit
    print(f"The {args.prop_name} of {args.dev_name} is {value} {unit if unit else ''}")

def set(args):
    api = init_api(args.auth_path)
    device = mijiaDevices(api, dev_name=args.dev_name)
    ret = device.set_v2(args.prop_name, args.value)
    unit = device.prop_list[args.prop_name].unit
    if ret:
        print(f"The {args.prop_name} of {args.dev_name} is set to {args.value} {unit if unit else ''}")
    else:
        print(f"Failed to set the {args.prop_name} of {args.dev_name} to {args.value}")


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
                    wifispeaker = mijiaDevices(api, dev_name=device['name'])
                    break
            if wifispeaker is None:
                raise ValueError("No wifispeaker found")
        else:
            wifispeaker = mijiaDevices(api, dev_name=args.wifispeaker_name)
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
