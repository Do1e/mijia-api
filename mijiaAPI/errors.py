# https://github.com/kekeandzeyu/ha_xiaomi_home/blob/main/custom_components/xiaomi_home/miot/i18n/zh-Hans.json
ERROR_CODE = {
    "-10000": "未知错误",
    "-10001": "服务不可用",
    "-10002": "参数无效",
    "-10003": "资源不足",
    "-10004": "内部错误",
    "-10005": "权限不足",
    "-10006": "执行超时",
    "-10007": "设备离线或者不存在",
    "-10020": "未授权OAuth2）",
    "-10030": "无效的token（HTTP）",
    "-10040": "无效的消息格式",
    "-10050": "无效的证书",
    "-704000000": "未知错误",
    "-704010000": "未授权（设备可能被删除）",
    "-704014006": "没找到设备描述",
    "-704030013": "Property不可读",
    "-704030023": "Property不可写",
    "-704030033": "Property不可订阅",
    "-704040002": "Service不存在",
    "-704040003": "Property不存在",
    "-704040004": "Event不存在",
    "-704040005": "Action不存在",
    "-704040999": "功能未上线",
    "-704042001": "Device不存在",
    "-704042011": "设备离线",
    "-704053036": "设备操作超时",
    "-704053100": "设备在当前状态下无法执行此操作",
    "-704083036": "设备操作超时",
    "-704090001": "Device不存在",
    "-704220008": "无效的ID",
    "-704220025": "Action参数个数不匹配",
    "-704220035": "Action参数错误",
    "-704220043": "Property值错误",
    "-704222034": "Action返回值错误",
    "-705004000": "未知错误",
    "-705004501": "未知错误",
    "-705201013": "Property不可读",
    "-705201015": "Action执行错误",
    "-705201023": "Property不可写",
    "-705201033": "Property不可订阅",
    "-706012000": "未知错误",
    "-706012013": "Property不可读",
    "-706012015": "Action执行错误",
    "-706012023": "Property不可写",
    "-706012033": "Property不可订阅",
    "-706012043": "Property值错误",
    "-706014006": "没找到设备描述"
}


class LoginError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"code: {code}, message: {message}")

class APIError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"code: {code}, message: {message}")

class DeviceNotFoundError(Exception):
    def __init__(self, did: str):
        super().__init__(f"未找到 did 为 '{did}' 的设备，请检查 did 是否正确")

class MultipleDevicesFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class DeviceGetError(Exception):
    def __init__(self, dev_name: str, name: str, code: int):
        super().__init__(f"获取设备 '{dev_name}' 的属性 '{name}' 时失败, code: {code}, message: {ERROR_CODE.get(str(code), '未知错误')}")

class DeviceSetError(Exception):
    def __init__(self, dev_name: str, name: str, code: int):
        super().__init__(f"设置设备 '{dev_name}' 的属性 '{name}' 时失败, code: {code}, message: {ERROR_CODE.get(str(code), '未知错误')}")

class DeviceActionError(Exception):
    def __init__(self, dev_name: str, name: str, code: int):
        super().__init__(f"执行设备 '{dev_name}' 的动作 '{name}' 时失败, code: {code}, message: {ERROR_CODE.get(str(code), '未知错误')}")

class GetDeviceInfoError(Exception):
    def __init__(self, device_model: str):
        super().__init__(f"获取设备型号 '{device_model}' 的设备信息失败")
