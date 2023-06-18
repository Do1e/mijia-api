import json
from .postData import postData


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
