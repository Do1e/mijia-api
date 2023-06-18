import os
import json
from .postData import postData
from .getRooms import getRooms


def getconsItems(save: bool, roomIdx=0) -> dict:
    """
	getconsItems(save, roomIdx=0) -> dict.
	@description:
	获取耗材列表
	-------
	@param:
	save: bool, 是否保存到文件./json/consItems.json中
	roomIdx: int, 房间索引(在./json/rooms.json中找到对应的房间索引，默认为0)
	-------
	@Returns:
	dict, 耗材列表的字典
	-------
	"""
    authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
    if os.path.exists('./json/rooms.json'):
        rooms = json.load(open('./json/rooms.json', 'r', encoding='utf-8'))
    else:
        rooms = getRooms(save)
    try:
        homeId = rooms['result']['homelist'][roomIdx]['id']
    except IndexError:
        print('房间号超出范围')
        return
    data = {"home_id": int(homeId), "owner_id": authorize['userId']}
    msg = postData('/v2/home/standard_consumable_items', data, authorize)
    consItems = json.loads(msg)
    if save:
        with open('./json/consItems.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(consItems, indent=4, ensure_ascii=False))
    return consItems
