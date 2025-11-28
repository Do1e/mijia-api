import logging

from mijiaAPI import mijiaAPI


logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

api = mijiaAPI(".mijia-api-data/auth.json")
print(api.available)
api.login() # 实际就是调用 QRlogin 方法
print(api.available)
print(api.get_homes_list())
