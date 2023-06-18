import json
from .postData import postData


def getRooms(save: bool) -> dict:
    """
	getRooms(save) -> dict.
	@description:
	获取房间列表
	-------
	@param:
	save: bool, 是否保存到文件./json/rooms.json中
	-------
	@Returns:
	dict, 房间列表的字典
	-------
	"""
    authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
    data = {"fg": False, "fetch_share": True, \
            "fetch_share_dev": True, "limit": 300, "app_ver": 7}
    msg = postData('/v2/homeroom/gethome', data, authorize)
    rooms = json.loads(msg)
    if save:
        with open('./json/rooms.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(rooms, indent=4, ensure_ascii=False))
    return rooms
