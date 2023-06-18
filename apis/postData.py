import requests
import random
from hashlib import sha256
import base64
import hmac


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
    request.headers['Cookie'] = 'PassportDeviceId=' + authorize['deviceId'] + ';userId=' + str(
        authorize['userId']) + ';serviceToken=' + serviceToken + ';'
    msg = request.post('https://api.io.mi.com/app' + uri, data=body)
    return msg.text
