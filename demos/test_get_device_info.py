import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import get_device_info

model = sys.argv[1] if len(sys.argv) > 1 else 'lumi.acpartner.mcn04'

info = get_device_info(model)

with open(f'demos/dev_info_example/{model}.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
