# 简介
提供python的api，可以使用代码直接控制米家设备的功能

只需要基本的python包即可使用


# 使用
* 开始使用的时候需要把config.json中的信息填好即可
* 使用参考demo_open_light.py文件
* `login.py`只需运行一次，便会将登陆信息保存到`./json/authorize.json`中，之后`api.py`会从中读取

理论上是可以通过修改scenes.json文件来更精细化的控制米家设备，但是其json的value没有给出详细的参数设置规则，目前没有扩展其功能
现在偷懒的方法是在手机上的米家app上设置然后通过名字进行调用方法来控制设备

[设置方法](http://studyofnet.com/136095239.html)

