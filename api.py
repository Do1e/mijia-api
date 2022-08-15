import requests
import random
from hashlib import sha256
import base64
import hmac
import json
import os

def postData(uri: str, data: dict, authorize: dict) -> None:
	data = str(data).replace("'", '"').replace('True', 'true').replace('False', 'false')
	try:
		serviceToken = authorize['serviceToken']
		securityToken = authorize['securityToken']
	except KeyError:
		print('serviceToken not found, Unauthorized')
		return
	tempStr = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	nonce = ''
	for i in range(16):
		nonce += tempStr[random.randint(0, len(tempStr) - 1)]
	signedNonce = generateSignedNonce(securityToken, nonce)
	signature = generateSignature(uri, signedNonce, nonce, data)
	body = {'_nonce': nonce, 'data': data, 'signature': signature}
	userAgent = 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'
	request = requests.session()
	request.cookies = requests.cookies.RequestsCookieJar()
	request.headers['User-Agent'] = userAgent
	request.headers['x-xiaomi-protocal-flag-cli'] = 'PROTOCAL-HTTP2'
	request.headers['Cookie'] = 'PassportDeviceId=' + authorize['deviceId'] + ';userId=' + str(authorize['userId']) + ';serviceToken=' + serviceToken + ';'
	msg = request.post('https://api.io.mi.com/app' + uri, data=body)
	return msg.text

def generateSignedNonce(secret: str, nonce: str) -> str:
	sha = sha256()
	sha.update(base64.b64decode(secret))
	sha.update(base64.b64decode(nonce))
	return base64.b64encode(sha.digest()).decode()

def generateSignature(uri: str, signedNonce: str, nonce: str, data: str) -> str:
	sign = uri + "&" + signedNonce + "&" + nonce + "&data=" + data
	mac = hmac.new(base64.b64decode(signedNonce), digestmod='sha256')
	mac.update(sign.encode('utf-8'))
	return base64.b64encode(mac.digest()).decode()


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
		with open('./json/devices.json', 'w') as f:
			f.write(json.dumps(devs, indent=4, ensure_ascii=False))
	return devs

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
	data = {"fg": False, "fetch_share" :True, \
		"fetch_share_dev": True, "limit": 300, "app_ver": 7}
	msg = postData('/v2/homeroom/gethome', data, authorize)
	rooms = json.loads(msg)
	if save:
		with open('./json/rooms.json', 'w') as f:
			f.write(json.dumps(rooms, indent=4, ensure_ascii=False))
	return rooms

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
		with open('./json/scenes.json', 'w') as f:
			f.write(json.dumps(scenes, indent=4, ensure_ascii=False))
	return scenes

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
		scenes = getRooms(False)
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
		with open('./json/consItems.json', 'w') as f:
			f.write(json.dumps(consItems, indent=4, ensure_ascii=False))
	return consItems

def getDevAtt(devs: list) -> dict:
	"""
	getDevAtt(devs) -> dict.
	@description:
	获取设备属性
	-------
	@param:
	devs: list, 参数列表
	-------
	@Returns:
	dict, 返回的设备属性字典
	-------
	"""
	authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
	data = {"params": devs}
	msg = postData('/miotspec/prop/get', data, authorize)
	res = json.loads(msg)
	return res

def setDevAtt(devs: list) -> str:
	"""
	setDevAtt(devs) -> dict.
	@description:
	设置设备属性
	-------
	@param:
	devs: list, 参数列表
	-------
	@Returns:
	dict, 返回信息
	-------
	"""
	authorize = json.load(open('./json/authorize.json', 'r', encoding='utf-8'))
	data = {"params": devs}
	msg = postData('/miotspec/prop/set', data, authorize)
	return msg

if __name__ == '__main__':
	# 获取设备列表
	# devs = getDevices(True)
	# print(devs)

	# 获取房间列表
	# rooms = getRooms(True)
	# print(rooms)

	# 获取场景列表
	# scenes = getScenes(True, 0)
	# print(scenes)

	# 执行手动场景
	# runScene('控制台灯')

	# 获取设备耗材
	# consItems = getconsItems(True)
	# print(consItems)

	# 参数说明
	# did: 设备ID
	# siid: 功能分类ID
	# piid: 设备属性ID
	# aiid: 设备方法ID
	# 从下述网站查询

	# 米家产品库
	# https://home.miot-spec.com/

	# 获取全部设备列表
	# 返回结果说明
	# name: 设备名称
	# did: 设备ID
	# isOnline: 设备是否在线
	# model: 设备产品型号, 根据这个去米家产品库查该产品相关的信息

	# 获取设备属性，一次请求多个
	# Atts = getDevAtt([{"did":"111111111","siid":2,"piid":1},{"did":"111111111","siid":2,"piid":2},
	# 	{"did":"111111111","siid":2,"piid":3},{"did":"111111111","siid":2,"piid":4}])
	# print(Atts)

	# 设置设备属性
	# res = setDevAtt([{"did":"111111111","siid":2,"piid":1,"value":True},{"did":"111111111","siid":2,"piid":2,"value":100},
	# 	{"did":"111111111","siid":2,"piid":3,"value":5000}])
	# print(res)

	pass