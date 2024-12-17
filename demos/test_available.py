import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)

print(api.available)
