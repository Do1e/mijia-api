import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import get_device_info

info = get_device_info('lumi.acpartner.mcn04')

with open('demos/dev_info_example/lumi.acpartner.mcn04.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
