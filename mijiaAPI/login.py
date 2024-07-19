from typing import Tuple
import hashlib
import json
import os
import random
import string
import time
from urllib import parse

from qrcode import QRCode
import requests

from .urls import msgURL, loginURL, qrURL
from .utils import defaultUA

class LoginError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f'Error code: {code}, message: {message}')

class mijiaLogin(object):
    def __init__(self):
        self.deviceId = ''.join(random.sample(string.digits + string.ascii_letters, 16))
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': defaultUA,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': f'deviceId={self.deviceId}; sdkVersion=3.4.1'
        })

    def _get_index(self) -> Tuple[requests.Session, dict]:
        ret = self.session.get(msgURL)
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get index page, {ret.text}')
        ret_data = json.loads(ret.text[11:])
        data = {'deviceId': self.deviceId}
        data.update({
            k: v for k, v in ret_data.items() \
            if k in ['qs', '_sign', 'callback', 'location']
        })
        return data

    def login(self, username: str, password: str) -> dict:
        """login with username and password
        mijiaLogin.login(username: str, password: str) -> dict
        -------
        @param
        username: str, xiaomi account username(email/phone number/xiaomi id)
        password: str, xiaomi account password
        -------
        @return
        dict, data for authorization, including userId, ssecurity, deviceId, serviceToken
        """
        data = self._get_index()
        post_data = {
            'qs': data['qs'],
            '_sign': data['_sign'],
            'callback': data['callback'],
            'sid': 'xiaomiio',
            '_json': 'true',
            'user': username,
            'hash': (hashlib.md5(password.encode()).hexdigest().upper() + '0' * 32)[:32],
        }
        ret = self.session.post(loginURL, data=post_data)
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to post login page, {ret.text}')
        ret_data = json.loads(ret.text[11:])
        if ret_data['code'] != 0:
            raise LoginError(ret_data['code'], ret_data['desc'])
        if 'location' not in ret_data:
            raise LoginError(-1, 'Failed to get location')
        auth_data = {
            'userId': ret_data['userId'],
            'ssecurity': ret_data['ssecurity'],
            'deviceId': data['deviceId'],
        }
        ret = self.session.get(ret_data['location'])
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get location, {ret.text}')
        cookies = self.session.cookies.get_dict()
        auth_data['serviceToken'] = cookies['serviceToken']
        self.auth_data = auth_data
        return auth_data

    @staticmethod
    def _print_qr(loginurl: str, box_size: int = 10) -> None:
        print('Scan the QR code below with Mi Home app')
        qr = QRCode(border=1, box_size=box_size)
        qr.add_data(loginurl)
        qr.make_image().save('qr.png')
        try:
            qr.print_ascii(invert=True, tty=True)
        except OSError:
            print('Failed to print QR code to terminal, please use the qr.png file in the current directory.')

    def QRlogin(self) -> dict:
        """login with QR code
        mijiaLogin.QRlogin() -> dict
        -------
        @return
        dict, data for authorization, including userId, ssecurity, deviceId, serviceToken
        """
        data = self._get_index()
        location = data['location']
        location_parsed = parse.parse_qs(parse.urlparse(location).query)
        params = {
            '_qrsize': 240,
            'qs': data['qs'],
            'bizDeviceType': '',
            'callback': data['callback'],
            '_json': 'true',
            'theme': '',
            'sid': 'xiaomiio',
            'needTheme': 'false',
            'showActiveX': 'false',
            'serviceParam': location_parsed['serviceParam'][0],
            '_local': 'zh_CN',
            '_sign': data['_sign'],
            '_dc': str(int(time.time() * 1000)),
        }
        url = qrURL + '?' + parse.urlencode(params)
        ret = self.session.get(url)
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get QR code URL, {ret.text}')
        ret_data = json.loads(ret.text[11:])
        if ret_data['code'] != 0:
            raise LoginError(ret_data['code'], ret_data['desc'])
        loginurl = ret_data['loginUrl']
        self._print_qr(loginurl)
        try:
            ret = self.session.get(ret_data['lp'], timeout=60, headers={'Connection': 'keep-alive'})
        except requests.exceptions.Timeout:
            raise LoginError(-1, 'Timeout, please try again')
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to wait for login, {ret.text}')
        ret_data = json.loads(ret.text[11:])
        if ret_data['code'] != 0:
            raise LoginError(ret_data['code'], ret_data['desc'])
        auth_data = {
            'userId': ret_data['userId'],
            'ssecurity': ret_data['ssecurity'],
            'deviceId': data['deviceId'],
        }
        ret = self.session.get(ret_data['location'])
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get location, {ret.text}')
        cookies = self.session.cookies.get_dict()
        auth_data['serviceToken'] = cookies['serviceToken']
        self.auth_data = auth_data
        if os.path.exists('qr.png'):
            os.remove('qr.png')
        return auth_data
