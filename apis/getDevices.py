import json
from .postData import postData


def getDevices(save: bool) -> dict:
    """
	getDevices(save) -> dict.
	@description:
	获取设备列表
	-------
	@param:
	save: bool, 是否保存到文件./json/devices.json中
	-------
	@Returns:
	dict, 设备列表的字典
	-------
	"""
    authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
    data = {"getVirtualModel": False, "getHuamiDevices": 0}
    msg = postData('/home/device_list', data, authorize)
    devs = json.loads(msg)
    if save:
        with open('./json/devices.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(devs, indent=4, ensure_ascii=False))
    return devs
