import json
import sys
sys.path.extend(['.', '..'])
from mijiaAPI import mijiaDevice, mijiaAPI

with open('jsons/auth.json') as f:
    auth = json.load(f)
api = mijiaAPI(auth)

# sleep_time is optional, default is 0.5
# get after set shuold be delayed for a while, or the result may be incorrect
device = mijiaDevice(api, dev_name='小米小爱音箱Play 增强版', sleep_time=2)
print(device)
device.run_action('execute-text-directive', _in=['空调调至26度', True])
                                                # 文本           静默执行
device.run_action('play-text', _in=['你好，我是小爱同学'])
