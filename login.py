import requests
import json
from hashlib import md5
import random

import config


def login(sid: str, user: str, pwd: str) -> dict:
	msgUrl = "https://account.xiaomi.com/pass/serviceLogin?sid=" + sid + "&_json=true"
	loginUrl = "https://account.xiaomi.com/pass/serviceLoginAuth2"
	tempStr = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	deviceId = ''
	for i in range(16):
		deviceId += tempStr[random.randint(0, len(tempStr) - 1)]
	authorize = {}
	userAgent = 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'
	request = requests.session()
	request.cookies = requests.cookies.RequestsCookieJar()
	request.headers['User-Agent'] = userAgent
	request.headers['Accept'] = '*/*'
	request.headers['Accept-Language'] = 'zh-tw'
	request.headers['Cookie'] = 'deviceId=' + deviceId + '; sdkVersion=3.4.1'
	msg = request.get(msgUrl)
	result = json.loads(msg.text[11:])
	body = {}
	body['qs'] = result['qs']
	body['sid'] = result['sid']
	body['_sign'] = result['_sign']
	body['callback'] = result['callback']
	body['user'] = user
	pwd = md5(pwd.encode()).hexdigest().upper()
	pwd += '0' * (32 - len(pwd))
	body['hash'] = pwd
	body['_json'] = 'true'
	msg = request.post(loginUrl, data=body)
	result = json.loads(msg.text[11:])
	if result['code'] != 0:
		authorize['code'] = result['code']
		authorize['message'] = result['desc']
		return authorize
	msg = request.get(result['location'])
	for item in msg.headers['Set-Cookie'].split(', '):
		item = item.split('; ')[0]
		item = item.split('=', maxsplit=1)
		authorize[item[0]] = item[1]
	authorize['code'] = 0
	authorize['sid'] = sid
	authorize['userId'] = result['userId']
	authorize['securityToken'] = result['ssecurity']
	authorize['deviceId'] = deviceId
	authorize['message'] = '成功'
	return authorize

if __name__ == '__main__':
	authorize = login("xiaomiio", config.user, config.pwd)
	print(authorize['message'])
	if authorize['code'] == 0:
		with open("./json/authorize.json", "w") as f:
			f.write(json.dumps(authorize, indent=4, ensure_ascii=False))