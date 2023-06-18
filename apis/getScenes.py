import os
import json
from .postData import postData
from .getRooms import getRooms


def getScenes(save: bool, roomIdx=0) -> dict:
    """
	getScenes(save, roomIdx=0) -> dict.
	@description:
	获取场景列表
	-------
	@param:
	save: bool, 是否保存到文件./json/scenes.json中
	roomIdx: int, 房间索引(在./json/rooms.json中找到对应的房间索引，默认为0)
	-------
	@Returns:
	dict, 场景列表的字典
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
    data = {"home_id": homeId}
    msg = postData('/appgateway/miot/appsceneservice/AppSceneService/GetSceneList', data, authorize)
    scenes = json.loads(msg)
    if save:
        with open('./json/scenes.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(scenes, indent=4, ensure_ascii=False))
    return scenes
