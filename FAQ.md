# 常见问题

## 账号密码登录失败

现在登录似乎100%遇到验证码，建议使用扫码登录。

## 扫码登录后的有效期多长？

`serviceToken` 有效期较短，但是已实现自动刷新。用于刷新的 `passToken` 有效期也许是一个月，即扫码登录后理论上可以保活一个月。

## XXX设备的XXX如何获取/设置？

我拥有的设备有限，无法保证能解答这类问题，但也欢迎提交 [issue](https://github.com/Do1e/mijia-api/issues)，可能需要你将设备共享给我进行抓包或者自行抓包给我提供请求和响应，提供har文件的话注意自行删除cookie等敏感信息。

## 如何抓包？

小米官方给了一个[抓包教程](https://iot.mi.com/new/doc/accesses/direct-access/extension-development/troubleshooting/packet_capture)，我没试过，不确定是否能行，如果抓包成功数据是加密的，可以使用 [decrypt/decrypt.py](decrypt/decrypt.py) 解密。

我自己的解决方案是使用一个获取了root的手机，安装 [reqable](https://reqable.com/zh-CN/) 进行抓包，导出 HAR 文件后使用 [decrypt/decrypt_har.py](decrypt/decrypt_har.py) 解密后导入电脑版的 reqable 查看。

## 是否可以支持设备回调？

理论上可以实现，但由于[ha_xiaomi_home 开源许可证](https://github.com/XiaoMi/ha_xiaomi_home/blob/main/LICENSE.md)的要求，将不会支持相关功能。
