import os
import json
from .postData import postData
from .getScenes import getScenes


def runScene(name: str) -> int:
    """
	runScene(name: str) -> int.
	@description:
	执行手动场景
	-------
	@param:
	name: str, 场景名称
	-------
	@Returns:
	0: 执行成功
	-1: 执行失败
	-------
	"""
    authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
    if os.path.exists('./json/scenes.json'):
        scenes = json.load(open('./json/scenes.json', 'r', encoding='utf-8'))
    else:
        scenes = getScenes(True)

    scenesList = scenes['result']['scene_info_list']
    for scene in scenesList:
        if scene['name'] == name:
            scene_id = scene['scene_id']
            break
    try:
        data = {"scene_id": scene_id, "trigger_key": "user.click"}
    except NameError:
        print("场景名称不存在")
        return -1
    msg = postData('/appgateway/miot/appsceneservice/AppSceneService/RunScene', data, authorize)
    msg = json.loads(msg)
    if msg['result']:
        return 0
    else:
        print(msg)
        return -1
