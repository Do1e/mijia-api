import time
import json
from apis import *


if __name__ == '__main__':
    # 获取设备列表
    devs = getDevices(save=True)
    print(devs)
    time.sleep(2)

    # 获取房间列表
    rooms = getRooms(save=True)
    print(rooms)
    time.sleep(2)

    # 获取场景列表
    scenes = getScenes(save=True, roomIdx=0)
    print(scenes)
    time.sleep(2)

    # 执行手动场景
    runScene('关灯')
    time.sleep(2)
    runScene('开灯')
    time.sleep(2)

    # 获取设备耗材
    consItems = getconsItems(True)
    print(consItems)
    time.sleep(2)

    # 参数说明
    # did: 设备ID
    # siid: 功能分类ID
    # piid: 设备属性ID
    # aiid: 设备方法ID
    # 从下述网站查询
    # 米家产品库，网站不稳定，不知道siid和piid无法使用`getDevAtt`和`setDevAtt`
    # 一个取巧的办法是使用在米家APP手动设置批量控制，然后使用`runScene`
    # https://home.miot-spec.com/

    # 获取全部设备列表函数`getDevices`返回结果说明
    # 返回结果说明
    # name: 设备名称
    # did: 设备ID
    # isOnline: 设备是否在线
    # model: 设备产品型号, 根据这个去米家产品库查该产品相关的信息

    # 获取设备属性，一次可以请求多个
    # Atts = getDevAtt([{"did":"111111111","siid":2,"piid":1},{"did":"111111111","siid":2,"piid":2},
    # 	{"did":"111111111","siid":2,"piid":3},{"did":"111111111","siid":2,"piid":4}])
    # print(Atts)
    # 例子
    with open('./json/devices.json', 'r', encoding='utf-8') as f:
        devs = json.load(f)
    myLight = None
    for dev in devs['result']['list']:
        if dev.get('model') == 'yeelink.light.lamp4':
            myLight = dev['did']
            break
    if myLight:
        isOpen = getDevAtt([{"did": myLight, "siid": 2, "piid": 1}]) # 获取台灯的开关状态
        if isOpen.get('code') == 0:
            if isOpen['result'][0]['value']:
                print('台灯已开启')
                status = getDevAtt([
                    {"did": myLight, "siid": 2, "piid": 2}, # 获取台灯的亮度
                    {"did": myLight, "siid": 2, "piid": 3}, # 获取台灯的色温
                ])
                if status.get('code') == 0:
                    print('台灯亮度为{}%，色温为{}K'.format(status['result'][0]['value'], status['result'][1]['value']))
                else:
                    print('获取台灯亮度和色温失败')
                setDevAtt([{"did": myLight, "siid": 2, "piid": 1, "value": False}]) # 关闭台灯
            else:
                print('台灯已关闭')
        else:
            print('获取台灯开关状态失败')
    time.sleep(2)

    # 设置设备属性
    # res = setDevAtt([{"did":"111111111","siid":2,"piid":1,"value":True},{"did":"111111111","siid":2,"piid":2,"value":100},
    # 	{"did":"111111111","siid":2,"piid":3,"value":5000}])
    # print(res)
    # 例子
    if myLight:
        res = setDevAtt([
            {"did": myLight, "siid": 2, "piid": 1, "value": True},  # 打开台灯
            {"did": myLight, "siid": 2, "piid": 2, "value": 100},  # 设置台灯亮度为100%
            {"did": myLight, "siid": 2, "piid": 3, "value": 5000},  # 设置台灯色温为5000K
        ])
        if res.get('code') == 0:
            print('设置台灯成功')
        else:
            print('设置台灯失败')
