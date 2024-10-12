import json
import os
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaLogin

if not os.path.exists('jsons'):
    os.mkdir('jsons')

api = mijiaLogin()
auth = api.QRlogin()
with open('jsons/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
