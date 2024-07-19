import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaLogin

api = mijiaLogin()
auth = api.QRlogin()
with open('jsons/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
