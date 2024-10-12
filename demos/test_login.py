import json
import os
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaLogin

if not os.path.exists('jsons'):
    os.mkdir('jsons')

username = os.getenv('XIAOMI_USERNAME')
password = os.getenv('XIAOMI_PASSWORD')
api = mijiaLogin()
auth = api.login(username, password)
with open('jsons/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
