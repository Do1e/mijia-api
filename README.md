* 提供Python的米家API
* 参考[janzlan/mijia-api](https://gitee.com/janzlan/mijia-api/tree/master)
* `login.py`运行前删除`import config`，并在`authorize = login("xiaomiio", config.user, config.pwd)`处填入账号密码
* `login.py`只需运行一次，便会将登陆信息保存到`./json/authorize.json`中，之后`api.py`会从中读取