import base64
from hashlib import sha256
import hmac
import random
import string

import requests

from .consts import apiURL


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


def post_data(session: requests.Session, ssecurity: str, uri: str, data: dict) -> dict:
    data = str(data).replace("'", '"').replace('True', 'true').replace('False', 'false')
    nonce = ''.join(random.sample(string.digits + string.ascii_letters, 16))
    signed_nonce = _generate_signed_nonce(ssecurity, nonce)
    signature = _generate_signature(uri, signed_nonce, nonce, data)
    post_data = {'_nonce': nonce, 'data': data, 'signature': signature}
    ret = session.post(apiURL + uri, data=post_data)
    if ret.status_code != 200:
        raise PostDataError(ret.status_code, f'发送数据失败, {ret.text}')
    ret_data = ret.json()
    return ret_data
