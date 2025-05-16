import hashlib
import json
import os
import random
import re
import string
import time
from datetime import datetime
from typing import Optional
from urllib import parse

import pytz
import requests
from qrcode import QRCode

from .logger import logger
from .urls import msgURL, loginURL, qrURL, accountURL
from .utils import defaultUA


class LoginError(Exception):
    def __init__(self, code: int, message: str):
        """
        初始化登录错误异常。

        Args:
            code (int): 错误代码。
            message (str): 错误消息。
        """
        self.code = code
        self.message = message
        super().__init__(f'Error code: {code}, message: {message}')


class mijiaLogin(object):
    def __init__(self, save_path: Optional[str] = None):
        """
        初始化米家登录对象。

        Args:
            save_path (str, optional): 认证数据保存路径。默认为None。
        """
        self.auth_data = None
        self.save_path = save_path

        self.deviceId = ''.join(random.sample(string.digits + string.ascii_letters, 16))
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': defaultUA,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': f'deviceId={self.deviceId}; sdkVersion=3.4.1'
        })

    def _get_index(self) -> dict[str, str]:
        """
        获取索引页数据。

        Returns:
            dict[str, str]: 包含设备ID和其他必要参数的字典。

        Raises:
            LoginError: 请求索引页失败时抛出。
        """
        ret = self.session.get(msgURL)
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get index page, {ret.text}')
        ret_data = json.loads(ret.text[11:])
        data = {'deviceId': self.deviceId}
        data.update({
            k: v for k, v in ret_data.items()
            if k in ['qs', '_sign', 'callback', 'location']
        })
        return data

    def _get_account(self, user_id: str) -> dict[str, str]:
        """
        获取账户信息。

        Args:
            user_id (str): 用户ID。

        Returns:
            dict[str, str]: 包含账户信息的字典。

        Raises:
            LoginError: 获取账户信息失败时抛出。
        """
        ret = self.session.get(accountURL + str(user_id))
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get account page, {ret.text}')
        ret_data = json.loads(ret.text[11:])['data']
        data = {
            k: v for k, v in ret_data.items()
            if k in ['account', 'gender', 'nickName', 'icon']
        }
        return data

    @staticmethod
    def extract_latest_gmt_datetime(data: dict) -> datetime:
        """
        提取过期时间并转换为中国时区。

        Args:
            data (dict): 用户凭证数据，包含GMT时间的键值对。

        Returns:
            datetime: 转换后的中国时区时间。

        Raises:
            LoginError: 如果没有找到GMT时间键或解析失败，抛出登录错误。
        """

        gmt_time_keys = [
            k for k in data.keys() if
            isinstance(k, str) and re.match(r'\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2} GMT', k)
        ]

        if not gmt_time_keys:
            raise LoginError(-1, 'No GMT time keys found in the data')

        parsed_times = [datetime.strptime(k, '%d-%b-%Y %H:%M:%S GMT') for k in gmt_time_keys]
        latest_utc_time = max(parsed_times)

        utc_zone = pytz.timezone('UTC')
        latest_utc_time = utc_zone.localize(latest_utc_time)

        china_zone = pytz.timezone('Asia/Shanghai')
        china_time = latest_utc_time.astimezone(china_zone)

        return china_time

    def _save_auth(self) -> None:
        """
        保存认证数据到文件。

        如果设置了保存路径且有认证数据，则将其以JSON格式保存到指定路径。
        """
        if self.save_path is not None and self.auth_data is not None:
            if not os.path.isabs(self.save_path):
                self.save_path = os.path.abspath(self.save_path)
            if os.path.exists(self.save_path) and not os.path.isfile(self.save_path):
                raise ValueError(f'Path [{self.save_path}] is not a file')
            if not os.path.exists(os.path.dirname(self.save_path)):
                os.makedirs(os.path.dirname(self.save_path))
            with open(self.save_path, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
            logger.info(f'Auth data saved to [{self.save_path}]')
        else:
            logger.info('Auth data not saved')

    def login(self, username: str, password: str) -> dict:
        """
        使用用户名和密码登录。

        Args:
            username (str): 小米账户用户名（邮箱/手机号/小米ID）。
            password (str): 小米账户密码。

        Returns:
            dict: 授权数据，包含userId、ssecurity、deviceId和serviceToken。

        Raises:
            LoginError: 登录失败时抛出。
        """
        logger.warning(
            'There is a high probability of verification code with account and password. Please try other login methods')
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
        if 'notificationUrl' in ret_data:
            raise LoginError(-1, 'Verification code required, please try other login methods')
        ret = self.session.get(ret_data['location'])
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get location, {ret.text}')
        cookies = self.session.cookies.get_dict()

        self.auth_data = {
            'userId': ret_data['userId'],
            'ssecurity': ret_data['ssecurity'],
            'deviceId': data['deviceId'],
            'serviceToken': cookies['serviceToken'],
            'expireTime': self.extract_latest_gmt_datetime(cookies).strftime('%Y-%m-%d %H:%M:%S'),
            **self._get_account(ret_data['userId'])
        }

        self._save_auth()
        return self.auth_data

    @staticmethod
    def _print_qr(loginurl: str, box_size: int = 10) -> None:
        """
        打印并保存二维码。

        Args:
            loginurl (str): 包含登录信息的URL。
            box_size (int, optional): 二维码大小。默认为10。
        """
        logger.info('Scan the QR code below with Mi Home app')
        qr = QRCode(border=1, box_size=box_size)
        qr.add_data(loginurl)
        qr.make_image().save('qr.png')
        try:
            qr.print_ascii(invert=True, tty=True)
        except OSError:
            qr.print_ascii(invert=True, tty=False)
            logger.info('If the QR code can not be scanned, '
                        'please change the font of the terminal, '
                        'such as "Maple Mono", "Fira Code", etc.\n'
                        'Or just use the qr.png file in the current directory.')

    def QRlogin(self) -> dict:
        """
        使用二维码登录。

        Returns:
            dict: 授权数据，包含userId、ssecurity、deviceId和serviceToken。

        Raises:
            LoginError: 登录失败时抛出。
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
        ret = self.session.get(ret_data['location'])
        if ret.status_code != 200:
            raise LoginError(ret.status_code, f'Failed to get location, {ret.text}')
        cookies = self.session.cookies.get_dict()

        self.auth_data = {
            'userId': ret_data['userId'],
            'ssecurity': ret_data['ssecurity'],
            'deviceId': data['deviceId'],
            'serviceToken': cookies['serviceToken'],
            'expireTime': self.extract_latest_gmt_datetime(cookies).strftime('%Y-%m-%d %H:%M:%S'),
            **self._get_account(ret_data['userId'])
        }

        self._save_auth()
        return self.auth_data

    def __del__(self):
        """
        析构函数，清理生成的二维码文件。
        """
        if os.path.exists('qr.png'):
            os.remove('qr.png')
