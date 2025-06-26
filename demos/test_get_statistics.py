import json
import time
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
with open('jsons/devices.json') as f:
    devices = json.load(f)
    did = devices[2]['did']
api = mijiaAPI(auth)
# 参考 https://iot.mi.com/new/doc/accesses/direct-access/extension-development/extension-functions/statistical-interface
ret = api.get_statistics({
    "did": did,
    "key": "7.1",                 # siid.piid，这里的7.1表示 lumi.acpartner.mcn04 的 power-consumption
    "data_type": "stat_month_v3", # 按月统计，可选：时（stat_hour_v3）、天（stat_day_v3）、星期（stat_week_v3）、月（stat_month_v3）
    "limit": 24,                  # 返回的最大条目数
    "time_start": 1685548800,     # 2023-06-01 00:00:00
    "time_end": 1750694400,       # 2025-06-24 00:00:00
})
"""
已知问题：
比较旧的设备使用的API会不一样，需要将`data_type`中的`_v3`去掉。
并且`key`也不一样，比如米家空调伴侣2的统计耗电量的`key`为`powerCost`。
详见 https://github.com/Do1e/mijia-api/issues/46
"""

for item in ret:
    value = eval(item['value'])[0]
    ts = item['time']
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    print(f'{date}: {value}')
