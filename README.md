# 历程
去年12月的时候就想过要搭一个telegramBot,也搭出来了，但功能不是很完善，所以想趁着最近比较闲加上有一个服务器来好好做。之前的文件有点乱，就重开了一个文件夹。

## 学到的东西
- 配置文件的读取
  ```python
    import json
    with open(config_path,'r') as f:
        config = json.load(f)
    
    proxy_url = config['proxy_url'] 
    token = config['token'] 
  ```

- 文件工作路径
  我的[bot.py](bot1.py)文件是存放在telegramBots这个文件夹中的，所以我就认为它的工作路径也就是这个文件夹，但出bug后发现是他的父文件夹
  ```python
  import os
  # 当前工作路径
  print(os.getcwd()) #D:\PythonLearning

  config_path = os.path.join(os.path.dirname(__file__),'config.json')
  ```
- logger
  