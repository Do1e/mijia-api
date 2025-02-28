import base64
from hashlib import sha256, md5
import hmac
import random
import string

import requests

from .urls import apiURL

defaultUA = 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'

class PostDataError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f'Error code: {code}, message: {message}')

def _generate_signed_nonce(secret: str, nonce: str) -> str:
    sha = sha256()
    sha.update(base64.b64decode(secret))
    sha.update(base64.b64decode(nonce))
    return base64.b64encode(sha.digest()).decode()


def _generate_signature(uri: str, signedNonce: str, nonce: str, data: str) -> str:
    sign = '&'.join([uri, signedNonce, nonce, f'data={data}'])
    mac = hmac.new(base64.b64decode(signedNonce), digestmod='sha256')
    mac.update(sign.encode())
    return base64.b64encode(mac.digest()).decode()

def _encrypt_password_md5(password: str) -> str:
    # decompile from mijia app v10.3.601
    digest = md5(password.encode()).digest()
    encrypted = ""
    for char in digest:
        i2 = (char & 240) >> 4
        encrypted += chr((i2 + 97) - 10 if (i2 < 0 or i2 > 9) else (i2 + 48))
        i3 = char & 15
        encrypted += chr((i3 + 97) - 10 if (i3 < 0 or i3 > 9) else (i3 + 48))
    encrypted = encrypted.upper()
    return encrypted

def post_data(session: requests.Session, ssecurity: str, uri: str, data: dict) -> dict:
    data = str(data).replace("'", '"').replace('True', 'true').replace('False', 'false')
    nonce = ''.join(random.sample(string.digits + string.ascii_letters, 16))
    signed_nonce = _generate_signed_nonce(ssecurity, nonce)
    signature = _generate_signature(uri, signed_nonce, nonce, data)
    post_data = {'_nonce': nonce, 'data': data, 'signature': signature}
    ret = session.post(apiURL + uri, data=post_data)
    if ret.status_code != 200:
        raise PostDataError(ret.status_code, f'Failed to post data, {ret.text}')
    ret_data = ret.json()
    return ret_data
