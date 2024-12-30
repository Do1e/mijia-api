import base64
from hashlib import sha256
import hmac
import random
import string

import requests
from lxml import etree
import json

from .urls import apiURL, deviceURL

defaultUA = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 Edg/126.0.0.0'

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
        raise PostDataError(ret.status_code, f'Failed to post data, {ret.text}')
    ret_data = ret.json()
    return ret_data

def _get_device_info(device_model: str) -> dict:
    response = response = requests.get(f'{deviceURL}{device_model}')
    html = etree.HTML(response.text)
    content = json.loads(str(html.xpath('//div[@id="app"]/@data-page')[0]))
    result = {}
    result['name'] = content['props']['product']['name']
    result['model'] = content['props']['product']['model']
    properties = []
    actions = []

    for siid in content['props']['spec']['services'].keys():
        if 'properties' in content['props']['spec']['services'][siid].keys():
            for piid in content['props']['spec']['services'][siid]['properties'].keys():
                properties.append({
                    'name': content['props']['spec']['services'][siid]['properties'][piid]['name'],
                    'description': content['props']['spec']['services'][siid]['properties'][piid]['description'],
                    'type': {
                        # https://iot.mi.com/v2/new/doc/introduction/knowledge/spec
                        'bool': 'bool',
                        'uint8': 'int',
                        'uint16': 'int',
                        'uint32': 'int',
                        'int8': 'int',
                        'int16': 'int',
                        'int32': 'int',
                        'int64': 'int',
                        'float': 'float',
                        'string': 'string',
                        'hex': 'hex'
                    }[content['props']['spec']['services'][siid]['properties'][piid]['format']],
                    'rw': ''.join([
                        'r' if 'read'  in content['props']['spec']['services'][siid]['properties'][piid]['access'] else '',
                        'w' if 'write' in content['props']['spec']['services'][siid]['properties'][piid]['access'] else '',
                    ]),
                    'unit': content['props']['spec']['services'][siid]['properties'][piid].get('unit', None),
                    'range': content['props']['spec']['services'][siid]['properties'][piid]['value-range'][:2] if 'value-range' in content['props']['spec']['services'][siid]['properties'][piid].keys() else None,
                    'method': {
                        'siid': siid,
                        'piid': piid
                    }
                })
        if 'actions' in content['props']['spec']['services'][siid].keys():
            for aiid in content['props']['spec']['services'][siid]['actions'].keys():
                actions.append({
                   'name': content['props']['spec']['services'][siid]['actions'][aiid]['name'],
                   'description': content['props']['spec']['services'][siid]['actions'][aiid]['description'],
                   'method': {
                      'siid': int(siid),
                      'aiid': int(aiid)
                   },
                   'in': [ { 'siid': siid, 'piid': in_piid } for in_piid in content['props']['spec']['services'][siid]['actions'][aiid]['in']]
                })
        

    result['properties'] = properties
    result['actions'] = actions

    return result