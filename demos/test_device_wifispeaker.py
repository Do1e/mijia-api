import logging

from mijiaAPI import mijiaAPI, mijiaDevice


logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

api = mijiaAPI(".mijia-api-data/auth.json")

# sleep_time 是可选的，默认是 0.5
# 设置后获取属性值时需要等待一段时间，否则可能获取到不正确的
device = mijiaDevice(api, dev_name='小米小爱音箱Play 增强版', sleep_time=1)
print(device)
device.run_action('execute-text-directive', _in=['打开空调', True])
                                                # 文本       是否静默执行
device.run_action('play-text', _in=['你好，我是小爱同学'])
