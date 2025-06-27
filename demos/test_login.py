import json
import os
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaLogin

if not os.path.exists('jsons'):
    os.mkdir('jsons')

# 此方法大概率需要手机验证码验证，建议优先使用二维码登录

username = os.getenv('XIAOMI_USERNAME')
password = os.getenv('XIAOMI_PASSWORD')
api = mijiaLogin()
auth = api.login(username, password)
with open('jsons/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
